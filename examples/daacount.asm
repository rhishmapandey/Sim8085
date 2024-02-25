mvi a, 00h
l1:
adi 01h ;adi bcoz inr doesn't affect all flags
daa
mov m, a
inx h
cpi 99h
jnz l1
hlt