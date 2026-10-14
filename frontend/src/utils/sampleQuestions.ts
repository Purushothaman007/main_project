import { Question } from '../types/question';

export const SAMPLE_QUESTIONS: Question[] = [
  {
    id: 'valid-parentheses',
    title: 'Valid Parentheses',
    difficulty: 'Easy',
    tags: ['Stack', 'String'],
    description: `Given a string \`s\` containing just the characters \`'('\`, \`')'\`, \`'{'\`, \`'}'\`, \`'['\` and \`']'\`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the **same type** of brackets.
2. Open brackets must be closed in the **correct order**.
3. Every close bracket has a corresponding open bracket of the same type.`,
    examples: [
      { input: 's = "()"',      output: 'true' },
      { input: 's = "()[]{}"',  output: 'true' },
      { input: 's = "(]"',      output: 'false' },
      { input: 's = "([])"',    output: 'true',  explanation: 'Properly nested.' },
    ],
    constraints: [
      '1 ≤ s.length ≤ 10⁴',
      's consists of parentheses only: \'()[]{}\''
    ],
    aiContext: `Problem: Valid Parentheses
Difficulty: Easy
Tags: Stack, String

Description:
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
Rules:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket.

Examples:
- s = "()" → true
- s = "()[]{}" → true
- s = "(]" → false
- s = "([])" → true

Constraints:
- 1 <= s.length <= 10^4
- s consists of parentheses only '()[]{}'

Key concept: Use a Stack data structure. Push opening brackets onto the stack; when a closing bracket is encountered, check if the top of the stack is the matching opening bracket.`,
  },
  {
    id: 'two-sum',
    title: 'Two Sum',
    difficulty: 'Easy',
    tags: ['Array', 'Hash Map'],
    description: `Given an array of integers \`nums\` and an integer \`target\`, return **indices** of the two numbers such that they add up to \`target\`.

You may assume that each input would have **exactly one solution**, and you may not use the same element twice.

You can return the answer in any order.`,
    examples: [
      { input: 'nums = [2,7,11,15], target = 9',  output: '[0,1]', explanation: 'nums[0] + nums[1] = 2 + 7 = 9.' },
      { input: 'nums = [3,2,4], target = 6',       output: '[1,2]' },
      { input: 'nums = [3,3], target = 6',         output: '[0,1]' },
    ],
    constraints: [
      '2 ≤ nums.length ≤ 10⁴',
      '-10⁹ ≤ nums[i] ≤ 10⁹',
      '-10⁹ ≤ target ≤ 10⁹',
      'Only one valid answer exists.'
    ],
    aiContext: `Problem: Two Sum
Difficulty: Easy
Tags: Array, Hash Map

Description:
Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.
Each input has exactly one solution. You may not use the same element twice.

Examples:
- nums = [2,7,11,15], target = 9 → [0,1]  (2+7=9)
- nums = [3,2,4], target = 6 → [1,2]
- nums = [3,3], target = 6 → [0,1]

Constraints:
- 2 <= nums.length <= 10^4
- Only one valid answer exists.

Key concept: Use a Hash Map (dictionary) to store each number's index as you iterate. For each element, check if (target - element) already exists in the map.`,
  },
  {
    id: 'reverse-linked-list',
    title: 'Reverse Linked List',
    difficulty: 'Easy',
    tags: ['Linked List', 'Recursion'],
    description: `Given the \`head\` of a singly linked list, reverse the list, and return the **reversed list**.`,
    examples: [
      { input: 'head = [1,2,3,4,5]', output: '[5,4,3,2,1]' },
      { input: 'head = [1,2]',       output: '[2,1]' },
      { input: 'head = []',          output: '[]' },
    ],
    constraints: [
      'The number of nodes in the list is in the range [0, 5000].',
      '-5000 ≤ Node.val ≤ 5000'
    ],
    aiContext: `Problem: Reverse Linked List
Difficulty: Easy
Tags: Linked List, Recursion

Description:
Given the head of a singly linked list, reverse the list and return the reversed head.

Examples:
- [1,2,3,4,5] → [5,4,3,2,1]
- [1,2] → [2,1]
- [] → []

Constraints:
- 0 to 5000 nodes
- -5000 <= Node.val <= 5000

Key concept: Iterative approach — use three pointers (prev, curr, next) to reverse the direction of each node's next pointer as you traverse the list.`,
  },
  {
    id: 'binary-search',
    title: 'Binary Search',
    difficulty: 'Easy',
    tags: ['Array', 'Binary Search'],
    description: `Given an array of integers \`nums\` which is sorted in ascending order, and an integer \`target\`, write a function to search \`target\` in \`nums\`. If \`target\` exists, then return its index. Otherwise, return \`-1\`.

You must write an algorithm with **O(log n)** runtime complexity.`,
    examples: [
      { input: 'nums = [-1,0,3,5,9,12], target = 9',  output: '4', explanation: '9 exists at index 4.' },
      { input: 'nums = [-1,0,3,5,9,12], target = 2',  output: '-1', explanation: '2 does not exist.' },
    ],
    constraints: [
      '1 ≤ nums.length ≤ 10⁴',
      '-10⁴ < nums[i], target < 10⁴',
      'All integers in nums are unique.',
      'nums is sorted in ascending order.'
    ],
    aiContext: `Problem: Binary Search
Difficulty: Easy
Tags: Array, Binary Search

Description:
Given a sorted integer array nums and a target, return the index of target or -1 if not found. Must run in O(log n).

Examples:
- nums = [-1,0,3,5,9,12], target = 9 → 4
- nums = [-1,0,3,5,9,12], target = 2 → -1

Constraints:
- 1 <= nums.length <= 10^4
- Array is sorted in ascending order.

Key concept: Maintain left and right pointers. Compute mid = (left+right)//2. Compare nums[mid] to target and narrow the search range accordingly.`,
  },
];
