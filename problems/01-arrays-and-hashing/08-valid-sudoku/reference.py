class Solution:
    def isValidSudoku(self, board):
        rows, cols, boxes = [set() for _ in range(9)], [set() for _ in range(9)], [set() for _ in range(9)]
        for r in range(9):
            for c in range(9):
                value = board[r][c]
                if value == '.':
                    continue
                b = (r // 3) * 3 + c // 3
                if value in rows[r] or value in cols[c] or value in boxes[b]:
                    return False
                rows[r].add(value); cols[c].add(value); boxes[b].add(value)
        return True
