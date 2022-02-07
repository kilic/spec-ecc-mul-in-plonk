Multiplication scripts emulate and specs out windowed batch and single ecc multiplication with a standart like PLONK gate. And analyze the cost in terms of row count. One can change operation costs in `ops.py` file and run scripts to see estimated and amortized costs per multiplication.

```
cost_double = 200
cost_add = 200
cost_ladder = 300
cost_select = 10  # five width equation with 2 multiplication gate
# cost_select = 23 # four width equation with 1 multiplication gate
```

``` 
> python mul.py # for single multiplication
> python mul_batch.py # for batch multiplication
```