def a(*args, **kwargs):
    print(f'args: {args}')
    print(f'kwargs: {kwargs}')

a(1, 2, a=1, b=2, c=3)