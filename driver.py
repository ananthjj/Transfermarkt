from average_recovery_index import injuryDataCreator
# this function was written by chat gpt
def check_input_type(input_str):
    try:
        # Try to convert the input string to an integer
        int(input_str)
        return "int"
    except ValueError:
        # If the above fails, it means the input string is not an integer
        return "str"
    
# this was written manually as the scraper was esentially destroying my computer 
# and using all the resources I had available
# written by Gabe
print("Please enter Y if you have a new text file to insert into the df")
YorN = input('y/n: ')
if YorN == "y" or YorN == "Y":
    player_info = input('filename: ')

    creator = injuryDataCreator(player_info)

    creator.load()

    print("Input a filename to save your data")
    save_info = input('filename: ')
    creator.save(save_info)
else:
    print("please insert a csv file to input")
    player_info = input('filename: ')
    creator = injuryDataCreator(player_info)
    creator.loadCsv(player_info)
dex = True
while dex:
    print("Would you like to enter a player's id or encoded name to get their average injury recovery index")
    YorN = input("Y/N: ")
    if YorN == "y" or YorN == "Y":
        print("Please enter the player's id or encoded name")
        encode = input("enter Id or Name: ")
        temp = check_input_type(encode)
        inputInt = None
        inputString = None
        if temp == "int":
            inputInt = encode
        else:
            inputString = encode
        text = creator.get(inputInt, inputString)
        print(text)
    else:
        dex = False


