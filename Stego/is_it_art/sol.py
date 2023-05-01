from PIL import Image
from math import sqrt
from binascii import unhexlify

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)

B_BLACK = 0
B_WHITE = 255

# Code128 start code
START_CODEA = '211412'
START_CODEB = '211214'
START_CODEC = '211232'

# Code128 symbols
ASCII_OFFSET = 32
CODE = ('212222', '222122', '222221', '121223', '121322', '131222', '122213', '122312', '132212', '221213', '221312', '231212', '112232', '122132', '122231', '113222', '123122', '123221', '223211', '221132', '221231', '213212', '223112', '312131', '311222', '321122', '321221', '312212', '322112', '322211', '212123', '212321', '232121', '111323', '131123', '131321', '112313', '132113', '132311', '211313', '231113', '231311', '112133', '112331', '132131', '113123', '113321', '133121', '313121', '211331', '231131', '213113', '213311', '213131', '311123', '311321', '331121', '312113', '312311', '332111', '314111', '221411', '431111', '111224', '111422', '121124', '121421', '141122', '141221', '112214', '112412', '122114', '122411', '142112', '142211', '241211', '221114', '413111', '241112', '134111', '111242', '121142', '121241', '114212', '124112', '124211', '411212', '421112', '421211', '212141', '214121', '412121', '111143', '111341', '131141', '114113, ', '114311', '411113', '411311', '113141', '114131', '311141', '411131', '211412', '211214', '211232', '233111', '211133', '2331112')

def center_logo(f, pix, W, H):
    # Get left offset (start of logo on the left)
    for x in range(W):
        if pix[x,H//2] != WHITE:
            offset_left = x
            break
    # Get right offset (start of logo on the right)
    for x in range(W-1, 0, -1):
        if pix[x,H//2] != WHITE:
            offset_right = W - x
            break
    # Get top offset (start of logo on the top)
    for y in range(H):
        if pix[H//2,y] != WHITE:
            offset_top = y
            break
    # Logo radius
    radius = (W - offset_left - offset_right) // 2
    # Logo center coordinates:
    c_x = radius + offset_left
    c_y = radius + offset_top
    return c_x, c_y, radius

def restore_barcode(f):
    # Open the image, load the pixels
    img = Image.open(f)
    pix = img.load()
    (W, H) = img.size

    # Logo is not quite cented in the image: find the logo center and its radius
    c_x, c_y, radius = center_logo(f, pix, W, H)
    # Mask the logo by zeroing all the pixel within a circle a little bit smaller than the logo itself
    # So that a bit of the barcode is left around
    c_logo = radius - 45
    c_border = radius - 30
    for x in range(W):
        for y in range(H):
            # Remove the logo and the border
            d = sqrt( (x - c_x)**2 + (y - c_y)**2)
            if d <= c_logo or d >= c_border:
                pix[x, y] = WHITE
    img.save("clean_" + f)

    # Now continue the lines of the barcode, by scanning the image line per line
    # If we detect color white (resp. black), we continue with white (resp. black)
    # We need to convert to black & white before though
    # Omg, there are two bar codes, one one the left, one on the right !!!
    img = img.convert('1')
    pix = img.load()
    for y in range(H):
        # Count the number of black / white pixels between then logo and the border circles
        # This is to identify the most probable color for the line
        # Do this once for the left barcode, once for the righr barcode
        count_left  = [0] * 2
        count_right = [0] * 2
        for x in range(W):
            d = sqrt( (x - c_x)**2 + (y - c_y)**2)
            if d > c_logo and d < c_border:
                p = int(pix[x, y]) // 255
                if x <= c_x:
                    count_left[p] += 1
                else:
                    count_right[p] += 1
        color_left  = count_left.index(max(count_left))
        color_right = count_right.index(max(count_right))
        # Continue the lines inside the logo with the most probable color found before, for both parts (left, right)
        for x in range(W):
            d = sqrt( (x - c_x)**2 + (y - c_y)**2)
            if x <= c_x:
                pix[x,y] = color_left
            else:
                pix[x,y] = color_right
    img.save("restored_" + f)
    return pix, W, H

def decode_barcode(barcode):
    # Count consecutive values and build code128, considering line thickness is approx. 4 pixels
    cur = ''; count = 0; code128 = ''
    for new in barcode:
        if new != cur and count != 0:
            code = round(count // 4)
            if code == 0:
                code = 1
            elif code == 5:
                code = 4
            code128 += str(code)
            count = 1
        else:
            count += 1
        cur = new
    code128 += str(count)

    # Shall be a multiple of 6, so truncate if not
    code128 = code128[:len(code128)//6*6]
    #print(code128, len(code128))

    # Identify which 128code this is: A, B or C
    start = code128[0:6]
    if start == START_CODEA:
        code_set = 'A'
    elif start == START_CODEB:
        code_set = 'B'
    elif start == START_CODEC:
        code_set = 'C'
    else:
        code_set = 'unknown'
        return
    #print('Detected 128code', code_set)
    # Skip start
    code128 = code128[6:]

    # Break code128 string into code128 characters
    l = [code128[x:x+6] for x in range(0, len(code128), 6)]
    print(l)

    # Omg, there are code changes...
    # 95 	5f 	US 	DEL 	95 	114113
    # 96 	60 	FNC 3 	FNC 3 	96 	114311
    # 97 	61 	FNC 2 	FNC 2 	97 	411113
    # 98 	62 	ShiftB 	ShiftA 	98 	411311
    # 99 	63 	Code C 	Code C 	99 	113141
    # 100 	64 	Code B 	FNC 4 	Code B 	114131
    # 101 	65 	FNC 4 	Code A 	Code A 	311141
    # (..)
    # 106 	6a 	Stop 	— 	— 	233111
    # 107               Stop inversé 	— 	211133
    # 108	 	Stop pattern            2331112
    s = ''
    print('Start Code', code_set)
    for x in l:
        if x in CODE:
            # Handle code set changes
            index = CODE.index(x)
            if index == 101:
                code_set = 'A'; print('Switch Code A')
            elif index == 100:
                code_set = 'B'; print('Switch Code B')
            elif index == 99 and code_set != 'C':
                code_set = 'C'; print('Switch Code C')
            elif index == 106:
                print('Code STOP')
                break
            elif index >= 95:
                print(x + "not expected")
            else:
                # Handle encoding, depending on code set
                if code_set == 'C':
                    # Code C: HEX
                    c = unhexlify(str(index)).decode()
                    print(c)
                    s += c
                else:
                    # Code A or B: ASCII
                    c = chr(index + ASCII_OFFSET)
                    print(c)
                    s += c

        else:
            print(x, 'not in CODE')
            break

    # Some more cheating: the brakets are hex-encoded; Also need to drop the last one apparently...
    print(s)
    s = s.replace('7b', '{')
    s = s.replace('7d', '}')
    s = s[: -1]
    print(s)
    return s

def extract_barcode(f, pix, W, H):
    # Extract the pixels on two vertical lines, one on the left, one on the right
    barcode_left = list(); barcode_right = list()
    for y in range(H):
        barcode_left.append(pix[0, y])
        barcode_right.append(pix[W-1, y])

    barcode_left  = barcode_left[203:672]  # Cheating here...
    barcode_right = barcode_right[203:672] # (..)
    barcode_right = barcode_right[::-1]    # Reverse the right part (seem to be down to top)

    print("RIGHT")
    dec_left  = decode_barcode(barcode_left)
    print("\nLEFT")
    dec_right = decode_barcode(barcode_right)
    print('\n')

    return dec_left + dec_right
    

def get_flag():
    logo = 'barcode-png.png'
    pix, W, H = restore_barcode(logo)
    return extract_barcode(logo, pix, W, H)

print(get_flag())
