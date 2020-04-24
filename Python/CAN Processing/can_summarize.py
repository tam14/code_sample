import os
import sys


class Channel:
    def __init__(self, offset: int, length: int, name: str):
        self.offset = offset
        self.length = length
        self.name = name.strip('\n')

    def __str__(self):
        return "offset: {}, length: {}, name: {}".format(self.offset, self.length, self.name)

    __repr__ = __str__

    def __lt__(self, other):
        return self.offset < other.length


class Message:
    def __init__(self, address: str, length: int, freq: int, channels: list):
        self.address = int(address, 16)
        self.length = length
        self.frequency = freq
        self.channels = channels

    def __str__(self):
        return "address: {}".format(hex(self.address))

    __repr__ = __str__

    def print_channels(self):
        for channel in self.channels:
            print(channel)

    def verify_message(self):
        bit_occupancy = list()
        unique_bit = set()
        for channel in self.channels:
            bit_occupancy.append(range(channel.offset, channel.offset + channel.length - 1, 1))
        for bit in bit_occupancy:
            if bit in unique_bit:
                unique_bit.add(bit)
            else:
                return False

        return True

    def __add__(self, other):
        self.channels.append(other)

    def __lt__(self, other):
        return self.address < other.address


if __name__ == "__main__":
    with open("transmit_all.txt", "r") as fp:
        idx = -1
        message_list = list()
        frequency = 0
        for line in fp:
            line_values = line.split(', ')
            if line_values[0] == 'bus':
                message_list.append(Message(line_values[1], line_values[2], frequency, list()))
                idx = idx + 1
            elif line_values[0] == 'hertz':
                frequency = line_values[1].strip()
            else:
                message_list[idx] + Channel(line_values[0], line_values[1], line_values[2])

        message_list.sort()

    for message in message_list:
        print(message)
        for channel in message.channels:
            print(channel)

    with open("ordered.csv", "w+") as fp:
        for message in message_list:
            for channel in message.channels:
                fp.write("{}, , {}, {}, {}, {}\n".format(hex(message.address), channel.offset, channel.length, message.frequency, channel.name))