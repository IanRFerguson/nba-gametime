#!/bin/python3

"""
Simple wrapper to instantiate Fan object
Sends text to the biggest fans you know

IRF
"""

from fan import Fan

def main():
      ian = Fan("NYK", "XXXXX")                             # Not my real number
      iriz = Fan("POR", "XXXXX")

      for big_homie in [ian, iriz]:
            big_homie.send_text()


if __name__ == "__main__":
      main()