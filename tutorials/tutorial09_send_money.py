"""
    This file is part of TON OS.

    TON OS is free software: you can redistribute it and/or modify
    it under the terms of the Apache License 2.0 (http://www.apache.org/licenses/)

    Copyright 2019-2021 (c) TON LABS
"""

'''

    This tutorial shows you how to send money
    and properly handle bounced messages.

'''


import sys
sys.path.append('../ts4_py_lib')
import ts4
from ts4 import eq


# Set a directory where the artifacts of the used contracts are located
ts4.set_tests_path('contracts/')

# Toggle to print additional execution info
ts4.set_verbose(True)

default_balance = 100*ts4.GRAM

# Deploy the sender's contract
tut09 = ts4.BaseContract('tutorial09', {})
addr_sender = tut09.address()

# Сheck the sender's initial balance. There are 100 grams by default
tut09.ensure_balance(default_balance)

# The contract address of the recipient
addr_recipient = '0:c4a31362f0dd98a8cc9282c2f19358c888dfce460d93adb395fa138d61ae5069'

# Сheck the recipient's balance. Until is not deployed it has no balance
assert eq(None, ts4.core.get_balance(addr_recipient))

# Send grams to the recipient with bounce flag
amount = ts4.GRAM
params = dict(addr = addr_recipient, amount = amount, bounce = True)
tut09.call_method('send_grams', params)

# Pick up internal message that was created by `send_grams()` call
msg_transfer = ts4.peek_msg()
assert eq(addr_sender, msg_transfer['src'])
assert eq(addr_recipient, msg_transfer['dst'])
assert eq(amount, msg_transfer['value'])

# Dispatch created message
ts4.dispatch_one_message()

# Сheck the sender's current balance
tut09.ensure_balance(default_balance - amount)

# Pick up internal message that was bounced
msg_bounced = ts4.peek_msg()
assert eq(addr_recipient, msg_bounced['src'])
assert eq(addr_sender, msg_bounced['dst'])
assert eq(True, msg_bounced['bounced'])
assert eq(amount, msg_bounced['value'])

# Dispatch bounced message
ts4.dispatch_one_message()

# Balance of the recipient should stay empty
assert eq(None, ts4.core.get_balance(addr_recipient))

# Send grams to the recipient without bounce flag
params = dict(addr = addr_recipient, amount = amount, bounce = False)
tut09.call_method('send_grams', params)

# Dispatch created message
ts4.dispatch_one_message()

# Check balance of the recipient, it should be equal to transferred amount
assert eq(amount, ts4.core.get_balance(addr_recipient))

# Сhecking the sender's balance, it should be decreased by the amount of the transfer
tut09.ensure_balance(default_balance - amount)