#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2021 Lazlo Westerhof <semaphore@lazlo.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Signal Bot example, get reward by sending photo to IPFS or verify the photo.
"""
import csv
import io
import json
import mimetypes
import logging
import os
import zipfile
from pathlib import Path

import anyio
import asks  # type: ignore
import feedparser  # type: ignore
import requests
from bs4 import BeautifulSoup  # type: ignore

from cai.jumbf import json_to_bytes
from cai.starling import Starling
from mobilecoin.client import Client
from semaphore import Bot, ChatContext


# Filepath of the latest received photo
Latest_photo = ''

# IPFS URL of the latest received photo
Latest_photo_url = 'https://ipfs.io./ipfs/defaultcid'

# Sender's phone number of the latest received photo
Latest_photo_source_number = ''

# When user send a message containing attachment and text,
# text will be treat as caption.
Latest_photo_caption = ''

# Verifier list. All the verifiers will get notifications to verify photos.
# The list contains verifiers' phone numbers.
Verifiers = []

# MobileCoin client instance
Mobilecoin = Client(url="http://127.0.0.1:9090/wallet", verbose=True)

# Content Creator Whitelist
Creator_whitelist = {
    # Zion
    '+447828564625': {
        'address': '3r7jnGv5tX9YhNajYPKczASHRbAn8xhvvy2KCAior8nK5AgAqBLYJEiUK7g56qweYytTxXAdvLCPgNwHdNjQFN2YojaDEYYr6uCPZVS8ffnGrzjbW7YxBXjsaCEotMEuo5MexEpGnxmVYJ49vgXBq8BzWR27u2FN6hSsu8LqbjLHqi3GRdhBDiHWAJt4q8ZsEWrx89JkU4dCMFTv7RkFRoCywZZjNjRkSmQuL8rEuLNr2d3F4'
    },
    # In-field 1
    '+447723327398': {
        'address': '52nJkToTAf4w8CeK6WZv3UxgnWWYZtcDmBwGmyT1LUiSsBXNL2DPYNENB9dbejajNMaZ8Kw5JCwBQPc9gFYVk21VEiJAzgF7dtd6czukcwou7uxdKyBB5xBk9FYv2gLth4Kw9ayKhc9P6aafaAsifqLK9xR7JNrdjH5Qu4GijS82swDoiJZrhczBL1bXQbKyNeiVbEntMjvjeWiKD8C8anakyf21CQxD8K9FGctMCZMaae15g'
    },
}

# Content Verifier Whitelist
Verifier_whitelist = {
    # Yui
    '+447380317516': {
        'address': '3ZvFiT6ud8Y33Cm9QRWdC8V8Lu5ea9RZwTdtABWNmrU8aPAs5k7CS46ejroJLDCHZhuUX5uq4CpQR5VYGC3HRvPRDFAbbXFxUPTCS1JpVghaH5uZvGY4NZdfPadqFt5zNzXtP9g3C9o6pKGExsf6uxnbWiDqyH9QTQiBP5G2Xdp3K2ypTL52GZRc5eLeWVGAki1XSc6VDSxGrgvCst624sVXqfWvepK7Ud95anGNjdgv61BXg'
    },
    # Jonathan, 2nd
    '+447723466379': {
        'address': '4E3quhtzVCEki1QRA6cYrCBczNcsvhQffNNDWmZsLC8KmRnLe6D3vDn1WZGyG2QRvWGSJgvEkcdfMd5AH168tLp4FGDWQBqNCKxqAgWTAiTJizddjKxraLCcyR6HDhMwQ5x2cdEUBtRB3wCMaC9gFHZKe6Hf6d2Ba9exvTgUVL3eXrHzS1zpvvP6ZXdUo7esPwoBG4JMnYeQtAn9MN6C4XUBnomXFmdUJLKBVBGgnYhABt7zJ'
    },
    # Rachel
    '+447578889560': {
        'address': '4ZgRSK4pJGuZHQutS2u8G4tEwrRUkdEuCZsbqh9AMyGM4fsKxyoGNFtLsWPzMbCKkNw2zrkP88LSRZVL5f3EJg76ANd9he6K6dpNfpUiKFDSHkjtuzASaG19cAaNvWFTACgHbK4TvdvkFf7Tm9JGuvN3yW3uXZLE5372BceJP9rvBA8YJ7uvzztAneQL4E7NXX98yMsAajxH9EZRKrjM6EQTHbFuFKeeU9jAh5j5GM4dFm276'
    },
    # Jihad
    '+447446258175': {
        'address': '4gBfa4fLxZWaA8zp8TjdSdqyJ87aRWY9AHUwdSFfvov6JL3d6iJf9pvXT7L7n81vJUwdz9tffWPd7rfWimyj4Vgsi4Qgk8NDadASEFjYPrQf3dsTDujZrL9Mof6Mi2d21h1UgeU3JUAEHwWT5BK4cGDwitgydNZuZk5F8hrqxkZqi4uWdJhmiKNE56uioL3uFB5jnTXR4zQozmxNN7XvwQmKmCuuUt1A2Du6XoABxgd1AQc5L'
    },
}


def ipfs_add(filepath, cid_version=1):
    """ Add file to IPFS via infura API """

    mimetypes.init()
    mimetype = mimetypes.guess_type(filepath)[0]

    if cid_version == 1:
        url = "https://ipfs.infura.io:5001/api/v0/add?cid-version=1&raw-leaves=false"
    else:
        url = "https://ipfs.infura.io:5001/api/v0/add?&raw-leaves=false"
    payload = {}
    files = [
      ('file', (os.path.basename(filepath), open(filepath, 'rb'), mimetype))
    ]
    headers = {}
    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files
    )
    ipfs_cid = json.loads(response.text)['Hash']
    return ipfs_cid


def parse_proofmode_zip_to_json(zipfilepath):
    with zipfile.ZipFile(zipfilepath) as myzip:
        for fname in myzip.namelist():
            # pick *.proof.csv
            if fname.endswith(".proof.csv"):
                with myzip.open(fname, mode="r") as csvfile:
                    csvdata = csvfile.read()
                    df = io.StringIO(csvdata.decode("utf-8"))
                    rows = csv.reader(df)

                    # Get headerRow and lastRow
                    headerRow = None
                    lastRow = None
                    for i in rows:
                        if (headerRow is None):
                            headerRow = i
                        if (len(headerRow) == len(i)):
                            lastRow = i

                    # Prepare dictionary to store json data
                    dict1 = {}
                    for i in range(len(headerRow)):
                        k = headerRow[i].strip()
                        k = k.replace(" ","")
                        if (not k):
                            continue
                        k = "proofmode:"+k
                        v = lastRow[i].strip()

                        dict1[k]=v

                    # Output json data
                    jsonData = json.dumps(dict1, indent=4)
                    return jsonData
            else:
                continue


def parse_proofmode_zip_to_photo(zipfilepath):
    with zipfile.ZipFile(zipfilepath) as myzip:
        for fname in myzip.namelist():
            # pick *.jpg
            if fname.endswith(".jpg"):
                with myzip.open(fname, mode="r") as f:
                    return f.read()
            else:
                continue


def cai_injection(photo_bytes, photo_filename, thumbnail_bytes, metadata=None):
    metadata = {
        'claim': {
            'store_label': 'cb.Authmedia_1',
            'recorder': '851b7b53-a987-4a2c-af3f-f3221028cca9',
        },
        'assertions': {
            'adobe.asset.info': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'title': photo_filename
                })
            },
            'cai.location.broad': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'location': 'Okura Garden Hotel, Shanghai'
                })
            },
            'cai.rights': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'copyright': 'Wing Shya'
                })
            },
            'cai.claim.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
            'cai.acquisition.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
            'starling.integrity.json': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'starling:PublicKey': 'fake-public-key',
                    'starling:MediaHash': 'd3554e727696c9c0a116491b4dc2006752361ad478d2fa742158ec2cd823b56e',
                    'starling:MediaKey': 'd3554e7276_1608464410000',
                    'starling:CaptureTimestamp': '2020-12-20T11:40:10Z'
                })
            }
        }
    }

    starling = Starling(photo_bytes,
                        photo_filename,
                        metadata['assertions'],
                        metadata['claim']['store_label'],
                        metadata['claim']['recorder'],
                        '',
                        '')
    photo_bytes = starling.cai_injection()

    # Save to file
    fname, fext = os.path.splitext('/tmp/cai-debug.jpg')
    fpath = fname + '-cai-cai-cai' + fext
    with open(fpath, 'wb') as f:
        f.write(photo_bytes)
    print('CAI file:', fpath)

    return fpath


async def ipfs(ctx: ChatContext) -> None:
    global Latest_photo
    global Latest_photo_url
    global Latest_photo_source_number
    global Latest_photo_caption
    global Verifiers
    global Mobilecoin

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("ctx.message: {}".format(ctx.message))
    print("data message: {}".format(ctx.message.data_message))
    print("message source number: {}".format(ctx.message.source.number))
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    #if len(ctx.message.data_message.body) == 0 and len(ctx.message.data_message.attachments) > 0:
    if len(ctx.message.data_message.attachments) > 0:
        Latest_photo_caption = ctx.message.data_message.body
        print('Attachment caption:', Latest_photo_caption)

        # Case: The bot receives a photo
        for attachment in ctx.message.data_message.attachments:
            print('Attachment type:', attachment.content_type)
            if attachment.content_type in ["image/png", "image/jpeg"]:
                print("Get PNG/JPEG stored at {}".format(attachment.stored_filename))
                Latest_photo = attachment.stored_filename
            elif attachment.content_type in ["application/zip"]:
                # Receive ProofMode, do CAI injection
                print("Get Zip stored at {}".format(attachment.stored_filename))
                proofmode_json = parse_proofmode_zip_to_json(attachment.stored_filename)
                print('ProofMode JSON', proofmode_json)

                Latest_photo = attachment.stored_filename

                # CAI injection
                photo_bytes = parse_proofmode_zip_to_photo(attachment.stored_filename)
                Latest_photo = cai_injection(photo_bytes, Latest_photo, photo_bytes, metadata=None)
            else:
                print('Unknown type', attachment.content_type)
                return
        # TODO: We only handle the latest photo currently.
        await ctx.message.reply(body="Do you want to archive the photo to IPFS? (y/n): ")
    elif len(ctx.message.data_message.body) > 0:
        # Case: The bot receives a message 

        # HACKING: /var/lib/signald/attachments/ permission
        # is 700 & signald:signald
        # change to 755

        cmd = ctx.message.data_message.body.split(' ')[0].lower()
        print('Command: ' + cmd)

        if len(Latest_photo) > 0:
            if ctx.message.data_message.body.lower() in ['y', 'yes']:
                cid = ipfs_add(Latest_photo)
                Latest_photo = ''
                Latest_photo_url = 'https://ipfs.io/ipfs/' + cid
                Latest_photo_source_number = ctx.message.source.number
                await ctx.message.reply(body="The photo has been archived to IPFS\n\nhttps://ipfs.io/ipfs/" + cid)

            else:
                Latest_photo = ''
                await ctx.message.reply(body="I will not archive the uploaded photo to IPFS")
        elif cmd == '/register':
            Verifiers.append(ctx.message.source.number)
            await ctx.message.reply(body=(
                '{} is a verifier now.\n\n'
                'Please send "/verify" to get the latest photo to verify.'.format(
                    ctx.message.source.number
                )
            ))
        elif cmd == '/verify':
            # get latest photo URL to verify
            if ctx.message.source.number in Verifiers:
                msg = (
                    'Please review the following photo:\n'
                    '{0}\n\n'
                    'Caption: {1}\n\n'
                    'Is the photo verified?\n\n'
                    'Yes: Please reply "/verified"\n'
                    'No: Please reply "/not-verified"'.format(
                        Latest_photo_url,
                        Latest_photo_caption)
                )
                await ctx.message.reply(body=msg)
            else:
                msg = (
                    'Welcome to the Hala Systems verification system.'
                    ' You are not yet registered as a user.\n\n'
                    'Would you like to register?\n\n'
                    'Please reply "/register" to start.'
                )
                await ctx.message.reply(body=msg)
        elif cmd == '/verified':
            # verified and agree authenticity of the photo for verification
            if ctx.message.source.number in Verifiers:
                msg = (
                    'Thank you.\n\n'
                    'This photo is marked as "verified".\n'
                    'CID: {0}'.format(
                        os.path.basename(Latest_photo_url)
                    )
                )
                await ctx.message.reply(body=msg)

                # send MobileCoin as rewards
                account_id = '492deddfd6feb224d839f8513407a75e7a90eeb21e10554f7bddc6b6ff29beb4'
                amount = 0.0006

                try:
                    to_address = Verifier_whitelist[ctx.message.source.number]['address']
                except Exception as e:
                    print('Number is not in Verifier whitelist:', ctx.message.source.number)

                try:
                    r = Mobilecoin.build_and_submit_transaction(account_id, amount, to_address)
                except Exception as e:
                    print('Fail to send MOB to verifier.')

                if Latest_photo_source_number in Creator_whitelist.keys():
                    print('Creator is in whitelist')
                    # WORKAROUND: use two wallets to prevent Txos error (issue #3)
                    account_id = 'f259dfdcd070e56315fb8fb0b528f3961a9c17247dcaa3aa8bba943ee1ffcf86'
                    amount = 0.0006

                    try:
                        to_address = Creator_whitelist[Latest_photo_source_number]['address']
                    except Exception as e:
                        print('Number is not in Creator whitelist:', Latest_photo_source_number)

                    try:
                        r = Mobilecoin.build_and_submit_transaction(account_id, amount, to_address)
                    except Exception as e:
                        print('Fail to send MOB to documentor.')
                else:
                    print('Creator is not in whitelist')

                msg = 'Payment has been sent to you and the documentor.'
                await ctx.message.reply(body=msg)

                print('Verifier number:', ctx.message.source.number)
                print('Content creator number:', Latest_photo_source_number)
            else:
                msg = 'You are not a verifier. Send "/register" to be a verifier'
                await ctx.message.reply(body=msg)
        elif cmd == '/not-verified':
            # verified and disagree authenticity of the photo for verification
            if ctx.message.source.number in Verifiers:
                msg = (
                    'Thank you.\n\n'
                    'This photo is marked as "not verified".\n'
                    'CID: {0}'.format(
                        os.path.basename(Latest_photo_url)
                    )
                )
                await ctx.message.reply(body=msg)

                # send MobileCoin as rewards
                account_id = '492deddfd6feb224d839f8513407a75e7a90eeb21e10554f7bddc6b6ff29beb4'
                amount = 0.0006

                try:
                    to_address = Verifier_whitelist[ctx.message.source.number]['address']
                except Exception as e:
                    print('Number is not in Verifier whitelist:', ctx.message.source.number)

                try:
                    r = Mobilecoin.build_and_submit_transaction(account_id, amount, to_address)
                except Exception as e:
                    print('Fail to send MOB to verifier.')

                #msg = 'Transaction result:\n' + json.dumps(r, indent=4)
                #await ctx.message.reply(body=msg)

                msg = 'Payment has been sent to you.'
                await ctx.message.reply(body=msg)

                print('Verifier number:', ctx.message.source.number)
            else:
                msg = 'You are not a verifier. Send "/register" to be a verifier'
                await ctx.message.reply(body=msg)
        elif cmd == '/mobtest':
            r = Mobilecoin.get_all_accounts()
            msg = 'All accounts: ' + json.dumps(r)
            await ctx.message.reply(body=msg)
        else:
            # echo
            await ctx.message.reply(body=ctx.message.data_message.body)
    else:
        print("Receive unknown message whose body and attachment are empty.")


async def main():
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"]) as bot:
        bot.register_handler("", ipfs)

        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    anyio.run(main)
