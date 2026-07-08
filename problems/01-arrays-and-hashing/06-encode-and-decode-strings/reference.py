class Solution:
    def encode(self, strs):
        return ''.join(f'{len(s)}#{s}' for s in strs)

    def decode(self, s):
        out = []
        i = 0
        while i < len(s):
            j = s.index('#', i)
            size = int(s[i:j])
            start = j + 1
            out.append(s[start:start + size])
            i = start + size
        return out
