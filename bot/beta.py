from bot.db import Users


db = Users()



keys = db.get_api_keys()

for key in keys:
    print(key[2])




"""print(f'{keys[0][1]} key: {keys[0][2]}')


print(f'{keys[1][1]} key: {keys[1][2]}')"""