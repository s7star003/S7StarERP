def numstr_to_ascii(numstr):
    # 假设每两位数字为一个ASCII码
    chars = []
    for i in range(0, len(numstr), 2):
        part = numstr[i:i+2]
        chars.append(chr(int(part)))
    return ''.join(chars)

if __name__ == "__main__":
    numstr = "1729445880229892043"
    ascii_str = numstr_to_ascii(numstr)
    print(f"原始数字: {numstr}")
    print(f"转换为ASCII: {ascii_str}")
