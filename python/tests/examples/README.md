These examples are extracted from the website:
https://www.verifysoft.com/en_example_mcdc.html

Test1
-----
The expression we evaluate is:
(A or B) and C


|Test case nº |  A  |  B  |  C  | (A or B) and C |
| :------------: | :----: | :----: | :----: | :----: |
| 1 | F | F | F | F |
| 2 | F | F | T | F |
| 3 | F | T | F | F |
| 4 | F | T | T | T |
| 5 | T | F | F | F |
| 6 | T | F | T | T |
| 7 | T | T | F | F |
| 8 | T | T | T | T |

For **Condition coverage** and **Decision coverage**, it's enough to evaluate test cases nº 1 and 8.

For **Modified condition/decision coverage** (MC/DC), it's enough to evaluate test cases nº 2, 3, 4 and 6.  

Test2
-----
The expression we evaluate is:
(A || B) && (C || D)

TODO: Complete

A: (u == 0)	B: (x>5)	C: (y<6)	D: (z == 0)	

|Test case nº |  A  |  B  |  C  |  D  | (A and B) and (C or D) |
|:------------: | :----: | :----: | :----: | :----: | :----: | 
| 1	| F |	| F |	| F |	| F |	| F |
| 2	| F |	| F |	| F |	| T |	| F |
| 3	| F |	| F |	| T |	| _ |	| F |
| 4	| F |	| T |	| F |	| F |	| F |
| 5	| F |	| T |	| F |	| T |	| T |
| 6	| F |	| T |	| T |	| _ |	| T |
| 7	| T |	| _ |	| F |	| F |	| F |
| 8	| T |	| _ |	| F |	| T |	| T |
| 9	| T |	| _ |	| T |	| _ |	| T |