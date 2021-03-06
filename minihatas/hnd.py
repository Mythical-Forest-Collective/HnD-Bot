from datetime import datetime

from hata import User, Embed

from ext.utils import dmsheet, InvalidSheetException, roll

# Initialise variables
BASE_STATS = ( # Autocomplete values
  "Undefined",
  "Strength",
  "Dexterity",
  "Constitution",
  "Intelligence",
  "Wisdom",
  "Charisma"
)

ROLLABLE_STATS = [
  *BASE_STATS,
]


# Events handler
@client.events
async def ready(client):
    await dmsheet.init()
    print(f"`{client:f}` is ready.")


@client.interactions(guild=guilds)
async def import_sheet(event, sheet_url:str, prnsoverride:str=None, vrbsoverride:str=None):
    """Imports a google sheet"""
    try:
        yield "Verifying sheet..."
        char = await chars.new_character(sheet_url, event.user.id, prnsoverride, vrbsoverride)
        if char:
            yield "Character successfully imported!"
            return
        yield "You already have a character linked to your account!"
        return
    except InvalidSheetException as e:
        del data[event.user.id]
        yield e


@client.interactions(guild=guilds)
async def unlink(event):
    """Unlinks a linked character sheet from your account. THIS IS PERMANENT."""
    char = chars.get(event.user.id)
    if char:
        del chars[event.user.id]
        yield "Successfully removed character."
        return
    yield "No character linked! If you'd like to link a new one, use the <`link`> command!"


@client.interactions(guild=guilds)
async def overview(event, user:('user', 'View another user\'s character sheet!')=None):
    """A brief overview of a character!"""
    if not user:
        user = event.user
    char = chars.get(user.id)
    if not char:
        yield "No character sheet linked! If you are trying to run this command on yourself, link a character sheet with the command!"
        return
    e = Embed(f"[__**Overview of {char.name}**__]", f"Here is a brief overview of {char.name}", color=0x224c3d, timestamp=datetime.now()).add_field("```⟩⟩⟩ Auto-generated description ⟨⟨⟨```", char.desc).add_author(user.avatar_url, f"Requested by {user.name}").add_thumbnail(char.image)
    yield e


@client.interactions(guild=guilds)
async def roll_dice(event, dice:('str', 'Use a format like `1d6` to roll 1 6-sided die'), stat:('str', 'Choose a value from the list!')="Undefined", mod:('str', 'Add a base to the stat')=0):
    """Roll dice!"""
    char = chars.get(event.user.id)
    if not char:
        yield "No character sheet linked! Link a character sheet with the link command!"
        return
    dice = dice.lower()
    stat = stat.title()
    res = roll(char, dice, mod)
    if stat not in ROLLABLE_STATS:
        yield f"{stat} isn't in the rollable stats, defaulting to `Undefined`! Rollable stats are: `{', '.join(ROLLABLE_STATS)}`"
        stat = "Undefined"
    if mod not in BASE_STATS:
        yield f"{mod} isn't a valid modifier, defaulting to `Undefined`! Valid modifiers are: `{', '.join(BASE_STATS)}`"
        mod = "Undefined"
    if res[1] and stat != "Undefined":
        yield f"Rolled a {dice} which has a value of {res[0]} for {stat}, with a modifier of {res[1]} for {mod}, for a total of {res[0]+res[1]}!"
    elif not res[1] and stat != "Undefined":
        yield f"Rolled a {dice} for a value of {res[0]} for {stat}!"
    elif res[1] and stat == "Undefined":
        yield f"Rolled a {dice} which has a value of {res[0]}, with a modifier of {res[1]} for {mod}, for a total of {res[0]+res[1]}!"
    elif not res[1] and stat == "Undefined":
        yield f"Rolled a {dice} which has a value of {res[0]}!"


@client.interactions(guild=guilds)
async def monster_dex(event, monster:str):
    """Use the MonsterDex to look through monsters in the campaign!"""
    yield
    await dmsheet.init()
    m = dmsheet.monsters.get(monster.title())
    if not m:
        yield f"`{monster}` isn't a valid monster! Choose one from the list!"
        return
    yield f"```yaml\n{m}```"


@client.interactions(guild=guilds)
async def reload_dm_sheet(event):
    """This command reloads the DM sheet"""
    if not dmsheet.is_dm(event.user.id):
        yield "You're not a DM and don't have access to this command!"
        return
    yield "Reloading DM sheet..."
    await dmsheet.reload()
    yield "DM sheet reloaded!"


@client.interactions(guild=guilds)
async def add_item(event, name:('str', 'Name of the item you wanna add')):
    """Allows the DM to add an item to the campaign at any point"""
    if not dmsheet.is_dm(event.user.id):
        yield "You're not a DM and don't have access to this command!"
        return
    yield "Not implemented yet!"


# Autocomplete
@roll_dice.autocomplete('stat')
async def stat_autocomplete(value):
    if value is None:
        return ROLLABLE_STATS
    return [ROLLABLE_STAT for ROLLABLE_STAT in ROLLABLE_STATS if value.title() in ROLLABLE_STAT]

@roll_dice.autocomplete('mod')
async def modifier_autocomplete(value):
    if value is None:
        return BASE_STATS
    return [BASE_STAT for BASE_STAT in BASE_STATS if value.title() in BASE_STAT]

@monster_dex.autocomplete('monster')
async def monster_autocomplete(value):
    if value is None:
        return dmsheet.MONSTER_LIST
    return [MONSTER for MONSTER in dmsheet.MONSTER_LIST if value.title() in MONSTER]
