#!/usr/bin/env python3

import discord
import asyncio
import sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Pipe
from complex_dice import *
from deck_of_many_things import *

HELP_STR = """
Hi, I'm Tymora! I evaluate complex dice expressions that have absolutely no use whatsoever!
These complex expressions are built out of numbers and operators, like mathematical expressions.

**The `.roll` Command**

General rules:

- Operators are infix, and are evaluated in decreasing order of precedence.
- If an operator gets a list where it expects a number, it uses the sum of the list.
- If an operator gets a number where it expects a list, it treats the number as a single-element list.

Operators:

In these descriptions, `a` refers to the left argument, and `b` refers to the right argument.

- `d`: Rolls `a` `b`-sided dice, and returns the sum. Precedence 4.
- `r`: Rerolls any `b`s in `a`, once. Precedence 3.
- `R`: Rerolls any `b`s in `a`, repeatedly, until no `b`s remain. Precedence 3.
- `t`: Takes the `b` lowest values from `a`. Precedence 3.
- `T`: Takes the `b` highest values from `a`. Precedence 3.
- `*`: Multiplies `a` and `b`. Precedence 2.
- `/`: Divides `a` by `b`, flooring the result. Precedence 2.
- `+`: Adds `a` and `b`. Precedence 1.
- `-`: Subtracts `b` from `a`. Precedence 1.
- `.`: Concatenates `a` and `b`. Precedence 1.
- `_`: Removes all elements in `b` from `a`. Precedence 1.
- `?`: Evaluates `b` if `a` is greater than 0, else returns 0. Precedence 0.

**Other Commands**

- `.count`: rolls a simple dice expression (`adb`), and counts how many of each number you get.
- `.help`: Sends you this help text in a DM.
- `.draw <ID>`: Draws a card from a Deck of Many Things with the specified ID.
- `.initdeck <ID> <1|0>: Initializes a Deck of Many Things with the specified ID.""" + \
 """ The second argument is 1 if a 22-card deck is to be used; otherwise 0."""

ZALGO_STR=\
    "Ḣ̥̪̗͙͚͉͓͔̎ͯ̃ͫͨͫ͜͠ͅẼ̖̼͍̞̘̠̫͛ ̳̤͗͛͆̉̈́̆̈͝C͚̱̮̘̆͂̌ͧŎ̧̟̞̩̳̝̘̯̂̂̀͐̆̏͞M̨̼͙̫̿͐̒̀̓̿ͅE͗̆͗͆̽͏͏̖̜̱͍̝̙ͅS͙̯͍̩̱̪̞ͦͣͫ͌̍ͦͤ͠ͅ"

GAME_STR = "1dbutter | .help"

MASTER = "YOUR DISCORD DISCRIMINATOR HERE"

banned_users = []

COMMAND_TIMEOUT = 5
MAX_MESSAGE_LENGTH = 2000

client = discord.Client()

executor = ProcessPoolExecutor()


def run_command(*args, **kwargs):
    fn = kwargs.pop('fn')
    conn = kwargs.pop('conn')
    conn.send(fn(*args, **kwargs))
    conn.close()


def do_command(fn, *args, **kwargs):
    parent_conn, child_conn = Pipe()
    kwargs['conn'] = child_conn
    kwargs['fn'] = fn
    p = Process(target=run_command, args=args, kwargs=kwargs)
    p.start()
    p.join(COMMAND_TIMEOUT)
    if p.is_alive():
        p.terminate()
        return "Request timed out"
    else:
        try:
            return parent_conn.recv()
        except:
            return "Error running command"


async def invoke_command(fn, *args, **kwargs):
    global executor
    result = executor.submit(do_command, fn, *args, **kwargs).result()
    return result


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    load_decks()
    await client.change_presence(game=discord.Game(name=GAME_STR))


@client.event
async def on_message(message):
    if str(message.author.discriminator) in banned_users:
        return
    elif message.content.startswith('.roll'):
        dice_str = message.content[6:]
        if dice_str == '0d0':
            await client.send_message(message.channel, "{} {}".format(message.author.mention, ZALGO_STR))
        else:
            result = await invoke_command(evaluate_dice, dice_str)
            if result is None:
                return
            response = "{} Result: {}".format(message.author.mention, result)
            if len(response) < MAX_MESSAGE_LENGTH:
                await client.send_message(message.channel, response)
            else:
                await client.send_message(message.channel, "{} Response too long".format(message.author.mention))
    elif message.content.startswith('.count'):
        dice_str = message.content[7:]
        if dice_str == '0d0':
            await client.send_message(message.channel, "{} {}".format(message.author.mention, ZALGO_STR))
        else:
            result = await invoke_command(roll_count, *map(int, dice_str.split('d')))
            response = "{} Result: {}".format(message.author.mention, result)
            if len(response) < MAX_MESSAGE_LENGTH:
                await client.send_message(message.channel, response)
            else:
                await client.send_message(message.channel, "{} Response too long".format(message.author.mention))
    elif message.content.startswith('.eval'):
        if str(message.author.discriminator) == MASTER:
            await client.send_message(message.channel, "{} {}".format(
                message.author.mention, eval(message.content[6:]))
            )
        else:
            await client.send_message(message.channel, "{} You're not the boss of me!".format(message.author.mention))
    elif message.content.startswith('.setgame'):
        if str(message.author.discriminator) == MASTER:
            await client.change_presence(game=discord.Game(name=message.content[9:]))
        else:
            await client.send_message(message.channel, "{} You're not the boss of me!".format(message.author.mention))
    elif message.content.startswith('.help'):
        await client.send_message(message.author, HELP_STR)
    elif message.content.startswith('.init'):
        deck_id, use_22 = message.content.split()[1:3]
        use_22 = int(use_22)
        init_deck(deck_id, use_22)
        await client.send_message(message.channel, "{} {}-card deck with ID {} initialized.".format(
            message.author.mention, 22 if use_22 else 13, deck_id)
        )
    elif message.content.startswith('.draw'):
        deck_id = message.content.split()[1]
        card = draw(deck_id)
        await client.send_message(message.channel, "{} Your card is: {}".format(message.author.mention, card))
    elif message.content.startswith('.butter'):
        await client.send_message(message.channel, "{} https://i.imgur.com/lue3ZfD.png".format(message.author.mention))


def main(client_secret, master):
    global client, MASTER
    MASTER = master
    client.run(client_secret)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: tymora <client secret> <master discriminator>")
    main(sys.argv[1], sys.argv[2])
