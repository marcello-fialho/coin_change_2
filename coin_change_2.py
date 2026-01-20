from typing import List, Callable
from functools import lru_cache

# A leetcode problem that has real use is coin change 2. Let's begin with the optimized bottom up solution
#
class Solution:
    def change(self, amount, coins):
        dp = [0] * (amount + 1)
        dp[0] = 1
        
        for coin in coins:
            for i in range(coin, amount + 1):
                dp[i] += dp[i - coin]
                
        return dp[amount]

# The solution is fine, it is optimal (time complexity is O(n*m), space complexity is O(n)) but I like recursion so let's try a recursive solution...
#     
class Solution1:
    def change(self, amount: int, coins: List[int]) -> int:
        def cc(amount_so_far, i):
            if amount_so_far == amount:
              return 1
            total_ways = 0
            for j in range(i, len(coins)):
              if amount_so_far + coins[j] <= amount:
                total_ways += cc(amount_so_far + coins[j], j) 
            return total_ways
        return cc(0, 0)

# This ^^ has horrible performance, let's add memoization...
#
class Solution2:
    def change(self, amount: int, coins: List[int]) -> int:
        cache = {}

        def cc(amount_so_far, i):
            state = (amount_so_far, i)
            if state in cache:
                return cache[state]
            if amount_so_far == amount:
                return 1
            
            total_ways = 0
            for j in range(i, len(coins)):
                if amount_so_far + coins[j] <= amount:
                    total_ways += cc(amount_so_far + coins[j], j)
            
            cache[state] = total_ways
            return total_ways

        return cc(0, 0)

# This ^^ is better, not as good a performer as the bottom up solution and will have stack overflow issues, but it is good on paper.
# But to be really useful a solution should return the combinations instead of the sum of the combinations.
# This next one is very knapsack like: 
#
class Solution3:
    def change(self, amount: int, coins: List[int]) -> List[List[int]]:
        # Convert coins to a tuple to make it hashable for lru_cache
        coins = tuple(coins)

        @lru_cache(None)
        def find_combinations(rem: int, start_index: int) -> List[tuple]:
            # Base Case: Successfully reached the amount
            if rem == 0:
                return [()]
            
            # Base Case: Exceeded amount or no more coins to pick
            if rem < 0 or start_index >= len(coins):
                return []

            # 1. Include the current coin (stay at the same index for reuse)
            # We take every combination returned and prepend the current coin
            include_current = [
                (coins[start_index],) + combination 
                for combination in find_combinations(rem - coins[start_index], start_index)
            ]

            # 2. Skip the current coin (move to the next index)
            exclude_current = find_combinations(rem, start_index + 1)

            # Return the combined results of both paths
            return include_current + exclude_current

        # Convert back to list of lists for the final output
        result = find_combinations(amount, 0)
        return [list(combination) for combination in result]

# The solution is good, it uses memoization, but I'd like it to be tail recursive... The next one is by Gemini.
#
class Solution4:
    def change(self, amount: int, coins: List[int]) -> List[List[int]]:
        # tr_cc is tail-recursive because its only action is calling itself.
        # It never waits for a child call to finish before returning.
        def tr_cc(worklist, results):
            # Base Case: No more paths left to explore
            if not worklist:
                return results

            # Get the current state (Remaining Amount, Coin Index, Current Path)
            rem, i, current_path = worklist.pop()

            # Success Case: Target amount reached
            if rem == 0:
                results.append(list(current_path))
                return lambda: tr_cc(worklist, results)

            # Failure Case: Exceeded amount or ran out of coins
            if rem < 0 or i >= len(coins):
                return lambda: tr_cc(worklist, results)

            # Branching: 
            # 1. Skip the current coin (move to next index)
            # 2. Use the current coin (stay at index i to allow reuse)
            worklist.append((rem, i + 1, current_path))
            
            new_path = current_path + (coins[i],)
            worklist.append((rem - coins[i], i, new_path))

            # The final action is purely a call to tr_cc via the trampoline
            return lambda: tr_cc(worklist, results)

        # The Trampoline prevents RecursionError by calling lambdas in a flat while loop
        def trampoline(f: Callable):
            result = f()
            while callable(result):
                result = result()
            return result

        # Initial state: (Target Amount, Index 0, Empty tuple for path)
        return trampoline(lambda: tr_cc([(amount, 0, ())], []))

# Gemini did this ^^. My point with this exercise is to show my interests.
#         
if __name__ == '__main__':
   print(Solution4().change(amount = 5, coins = [1, 2, 5]))
