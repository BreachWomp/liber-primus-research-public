"""Explicit reversible repeating-key schedules, including copied F runes."""
from .alphabet import validate_indices


def primitive(key):
    key=validate_indices(key)
    if not key:raise ValueError('Nonempty key required')
    for size in range(1,len(key)+1):
        if len(key)%size==0 and key[:size]*(len(key)//size)==key:return key[:size]


def schedule(values,period,skips=()):
    values=validate_indices(values)
    if type(period) is not int or period<1:raise ValueError('Positive integer period required')
    skips=list(skips)
    if len(set(skips))!=len(skips) or any(type(i) is not int or not 0<=i<len(values) for i in skips):
        raise ValueError('Unique valid skip positions required')
    if any(values[i]!=0 for i in skips):raise ValueError('Only F may be copied')
    copied=set(skips);cursor=0;slots=[]
    for i in range(len(values)):
        if i in copied:slots.append(-1)
        else:slots.append(cursor%period);cursor+=1
    return slots


def decrypt(values,key,sign=1,skips=()):
    values=validate_indices(values);key=validate_indices(key)
    if not key or type(sign) is not int or sign not in (-1,1):raise ValueError('Invalid key/sign')
    return [0 if slot<0 else (sign*x+key[slot])%29
            for x,slot in zip(values,schedule(values,len(key),skips))]


def encrypt(values,key,sign=1,skips=()):
    values=validate_indices(values);key=validate_indices(key)
    if not key or type(sign) is not int or sign not in (-1,1):raise ValueError('Invalid key/sign')
    return [0 if slot<0 else (sign*(x-key[slot]))%29
            for x,slot in zip(values,schedule(values,len(key),skips))]
