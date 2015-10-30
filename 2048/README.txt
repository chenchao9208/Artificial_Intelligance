

Name: Chao Chen
UNI: cc3736
Email: cc3736@columbia.edu


#######################################################################################################
	HW2: Adversarial Search solution description
#######################################################################################################

The solutions of PlayerAI and ComputerAI are based on minimax and alpha-beta pruning,
as well as some tips to improve the performance. Since the PlayerAI and ComputerAI work symmetrically,
Here PlayerAI is described in details.

The introduction includes several parts:
	1. Method description.
	2. Implementation tips.
	3. Result statistics.


#######################################################################################################
	1.Methods description:
#######################################################################################################
getMove():
	Get a suggested move after calculation.

alpha_beta_search():
	The invoker of minimax alpha-beta-search.

max_value():
	The “max” level of minimax. Used Iteratively with ”min_value()”.

min_value():
	The “min” level of minimax. Used Iteratively with “max_value()”.

need_pruning():
	A slight extra pruning applied on “max” node, apart from alpa-beta-pruning

extra_pruning():
	Extra pruning applied on “min” node, apart from alpha-beta pruning.

f():
	key-retrieve function used to sort a list.

evaluate():
	evaluate a grid based on several weighted factors, as well as a punish-and-bonus procedure.

evaluation factors:
	monotonicity()
	smoothness()
	maxValue()
	space()

islands() & update_mask():
	Used for extra pruning

punish_and_bonus():
	extra part from weighted evaluation factor. So critical factors will affect the result heavily(not linearly weighted)


#######################################################################################################
	2.Implementation Tips
#######################################################################################################
1. Employ ITERATIVE DEEPENING DEPTH_FIRST alpha-beta-search, with DYNAMIC TIME LIMITATION.
	Since the search time is limited to 1s per step. The time complexity of solution is very important. On the one hand we want to search as deep as possible, on the other hand, we worry about the exponential time increase with the increase of search depth. 
	Thus, iterative deepening depth-first search is employed here, with a dynamic time limitation: if the potential “branch” is large, hold tight of the time limitation, otherwise loose the constraints.

2. EXTRA PRUNING apart from alpha-beta-pruning
	On “min” node to insert a cell by computer. The branch factor could vary from 1 to 15. When branch factor is large, alpha-beta-pruning could be not as efficient because it’s supposed to search into deep, which is lagged by the large branch factor at each level.
	Thus extra pruning is employed on “min” node to reduce the branch factor and help search deeper.

3. PUNISH_AND_BONUS processed apart from linearly weighted evaluation factors.
	Evaluation result is very important. Since we cannot search too deep due to several reasons(e.g. Step time constraint, unoptimized data structure, run time constraint of python language… ). We need a perfect evaluation result to compensate this and help “fore-see” the future results.
	The evaluation will be more important when facing large tiles, such as mergence of “128-128-256-512-1024-2048” into a single “4096”. The process takes 5 steps(max) and 9 levels(max-min-max…) on search tree, which cannot be fore-seen under current condition(7 levels per step is very high.) During the process of mergence, the value of “Monotonicity” is very possible to decrease. Since it doesn’t know the result of the process is to merge into a 4096(9-level is beyond its search depth), the “maxValue” factor(4096 is larger than 2048) will not be triggered, and the initial move to merge will be abandoned, because “Monotonicity” is violated, and total evaluation value is low.
	PUNISH_AND_BONUS is used to deal with the shortness of evaluation. For example: it weights tiles as: {256:16, 512:34…}. Value of “512”(34) is larger than twice the value of “256”(32=2*16), so it will force the tiles to be merged.


#######################################################################################################
	3.Result statistics
#######################################################################################################
I’ve tested PlayerAI.py for 20 times and get the following results:

	MaxTile | Count | Percentage 
	 512	|   1	|	5%
	 1024	|   4	|	20%
	 2048	|  12 	|	60%
	 4096	|   3	|	15%

