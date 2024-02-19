mvi a, 00h
l1:
adi 01h ;adi bcoz inr doesnot affect all flags
mov c, a
daa
mov m, a
mov a, c
inx h
cpi 99h
jnz l1
hlt