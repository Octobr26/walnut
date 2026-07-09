from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SAMPLE_BUNDLE = (
    'const _=["Arrays & Hashing","Two Pointers"];'
    'const $=[{problem:"Contains Duplicate",pattern:"Arrays & Hashing",'
    'link:"contains-duplicate/",difficulty:"Easy",code:"0217-contains-duplicate",'
    'neetcode150:!0,ncLink:"duplicate-integer/"},'
    '{problem:"Concatenation of Array",pattern:"Arrays & Hashing",'
    'link:"concatenation-of-array/",difficulty:"Easy",code:"1929-concatenation-of-array",'
    'neetcode250:!0,ncLink:"concatenation-of-array/"},'
    '{problem:"Two Sum II Input Array Is Sorted",pattern:"Two Pointers",'
    'link:"two-sum-ii-input-array-is-sorted/",difficulty:"Medium",'
    'code:"0167-two-sum-ii-input-array-is-sorted",neetcode150:!0,'
    'ncLink:"two-integer-sum-ii/"}];'
)


class NeetCodeMetadataTests(unittest.TestCase):
    def test_extracts_only_neetcode_150_public_metadata(self):
        from walnut.neetcode import extract_neetcode_150

        items = extract_neetcode_150(SAMPLE_BUNDLE)

        self.assertEqual([item.leetcode for item in items], [217, 167])
        self.assertEqual(items[0].title, "Contains Duplicate")
        self.assertEqual(items[0].topic, "Arrays & Hashing")
        self.assertEqual(items[0].leetcode_url, "https://leetcode.com/problems/contains-duplicate/")
        self.assertEqual(items[0].neetcode_url, "https://neetcode.io/problems/duplicate-integer")
        self.assertEqual(items[1].title, "Two Sum II Input Array Is Sorted")

    def test_string_decoder_preserves_non_ascii_and_expands_known_escapes(self):
        from walnut.neetcode import extract_neetcode_150

        bundle = (
            'const $=[{problem:"Caf\\u00e9 \\"Pair\\" \\\\ Test",'
            'pattern:"Arrays & Hashing",link:"cafe-pair/",difficulty:"Easy",'
            'code:"0001-cafe-pair",neetcode150:!0,ncLink:"cafe-pair/"}];'
        )

        items = extract_neetcode_150(bundle)

        self.assertEqual(items[0].title, 'Caf\u00e9 "Pair" \\ Test')

    def test_diff_reports_local_metadata_drift_without_statements(self):
        from walnut.neetcode import RoadmapProblem, diff_roadmap_metadata

        roadmap = {
            "topics": [
                {
                    "name": "Two Pointers",
                    "problems": [
                        {
                            "id": 11,
                            "title": "Two Sum II",
                            "difficulty": "Medium",
                            "leetcode": 167,
                            "leetcode_url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/",
                        }
                    ],
                }
            ]
        }
        scraped = [
            RoadmapProblem(
                order=1,
                title="Two Sum II Input Array Is Sorted",
                topic="Two Pointers",
                difficulty="Medium",
                leetcode=167,
                leetcode_url="https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/",
                neetcode_url="https://neetcode.io/problems/two-integer-sum-ii",
                code="0167-two-sum-ii-input-array-is-sorted",
            )
        ]

        diffs = diff_roadmap_metadata(roadmap, scraped)

        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]["field"], "title")
        self.assertEqual(diffs[0]["local"], "Two Sum II")
        self.assertEqual(diffs[0]["scraped"], "Two Sum II Input Array Is Sorted")


if __name__ == "__main__":
    unittest.main()
