from cs50 import get_int


def main():

    # Almost an exact copy of the "c" version. I understand that I could
    # "abstractize" this more due to the high level nature of Python.
    # However I am busy this week and have less time to dedicate to this than I would like.

    cc_number = get_int("Number: ")
    lun_calc(cc_number)

    lun = lun_calc(cc_number)
    lun_validity = lun_val(lun)
    card = card_check(cc_number)

    if(lun_validity and card == 1):
        print("AMEX")
    elif(lun_validity and card == 2):
        print("MASTERCARD")
    elif(lun_validity and card == 3):
        print("VISA")
    else:
        print("INVALID")


def lun_calc(cc_number):
    cc_number = str(cc_number)
    l = len(cc_number)
    sum = 0
    lun1 = 0
    lun2 = 0

    for i in range(l):
        if((l - i) % 2 == 0):  # If every second number
            digit = int(cc_number[i]) * 2  # multiply by 2
            digit2 = str(digit)
            l2 = len(digit2)
            for j in range(l2):  # split the digit number if required.
                digit3 = int(digit2[j])
                lun1 = lun1 + digit3  # add the numbers.
        else:
            lun2 = lun2 + int(cc_number[i])

    lun = lun1 + lun2

    return lun


def lun_val(lun):

    # Check if lun ends with 0, if yes output true.
    if (lun % 10 == 0):
        return True
    else:
        return False


def card_check(cc_number):
    cc_number = str(cc_number)
    digit1 = int(cc_number[0])
    digit2 = int(cc_number[1])

    l = len(str(cc_number))

    # Check length and start digit and output the correct card.
    if (l == 15 and digit1 == 3 and (digit2 == 4 or digit2 == 7)):
        return 1  # AMEX
    elif (l == 16 and digit1 == 5 and (digit2 == 1 or digit2 == 2 or digit2 == 3 or digit2 == 4 or digit2 == 5)):
        return 2  # MASTERCARD
    elif ((l == 16 and digit1 == 4) or (l == 13 and digit1 == 4)):
        return 3  # VISA
    else:
        return 0  # INVALID


main()
