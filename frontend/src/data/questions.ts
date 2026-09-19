import { Question } from '../types/question';

export const STATIC_QUESTIONS: Question[] = [
  {
    id: 'two-sum',
    title: 'Two Sum',
    difficulty: 'Easy',
    topic: 'Array / Hashing',
    shortDescription: 'Find two indices whose values add up to the target.',
    description:
      'Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.',
    inputFormat: 'nums = [2,7,11,15], target = 9',
    outputFormat: '[0,1]',
    examples: [
      {
        input: 'nums = [2,7,11,15], target = 9',
        output: '[0,1]',
        explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].',
      },
      {
        input: 'nums = [3,2,4], target = 6',
        output: '[1,2]',
        explanation: 'Because nums[1] + nums[2] == 6, we return [1, 2].',
      },
    ],
    constraints: [
      '2 <= nums.length <= 10^4',
      '-10^9 <= nums[i] <= 10^9',
      '-10^9 <= target <= 10^9',
      'Only one valid answer exists.',
    ],
    starterCode: {
      python: `def two_sum(nums, target):
    # Write your solution here
    pass

if __name__ == '__main__':
    nums = [2, 7, 11, 15]
    target = 9
    print(two_sum(nums, target))
`,
      java: `import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        // Write your solution here
        return new int[]{};
    }

    public static void main(String[] args) {
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        int[] result = twoSum(nums, target);
        System.out.println(Arrays.toString(result));
    }
}
`,
      cpp: `#include <iostream>
#include <vector>

using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your solution here
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    int target = 9;
    vector<int> result = twoSum(nums, target);
    cout << "[" << result[0] << ", " << result[1] << "]" << endl;
    return 0;
}
`,
    },
  },
  {
    id: 'reverse-linked-list',
    title: 'Reverse Linked List',
    difficulty: 'Easy',
    topic: 'Linked List',
    shortDescription: 'Reverse a singly linked list and return its head.',
    description:
      'Given the head of a singly linked list, reverse the list, and return the reversed list.',
    inputFormat: 'head = [1,2,3,4,5]',
    outputFormat: '[5,4,3,2,1]',
    examples: [
      {
        input: 'head = [1,2,3,4,5]',
        output: '[5,4,3,2,1]',
        explanation: 'The pointers are reversed to point backwards.',
      },
      {
        input: 'head = [1,2]',
        output: '[2,1]',
        explanation: 'Head points to 2, which points to 1.',
      },
    ],
    constraints: [
      'The number of nodes in the list is in the range [0, 5000].',
      '-5000 <= Node.val <= 5000',
    ],
    starterCode: {
      python: `class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    # Write your solution here
    pass

if __name__ == '__main__':
    head = ListNode(1, ListNode(2, ListNode(3)))
    curr = reverse_list(head)
    while curr:
        print(curr.val, end=' ')
        curr = curr.next
`,
      java: `class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}

public class Main {
    public static ListNode reverseList(ListNode head) {
        // Write your solution here
        return null;
    }

    public static void main(String[] args) {
        System.out.println("Reverse Linked List Initialized");
    }
}
`,
      cpp: `#include <iostream>

struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(nullptr) {}
};

ListNode* reverseList(ListNode* head) {
    // Write your solution here
    return nullptr;
}

int main() {
    std::cout << "Reverse Linked List Initialized" << std::endl;
    return 0;
}
`,
    },
  },
  {
    id: 'valid-parentheses',
    title: 'Valid Parentheses',
    difficulty: 'Easy',
    topic: 'Stack / String',
    shortDescription:
      'Determine if the input string has valid open and closed brackets.',
    description:
      'Given a string `s` containing just the characters `\'(\'`, `\')\'`, `\'{\'`, `\'}\'`, `\'[\'` and `\']\'`, determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.',
    inputFormat: 's = "()[]{}"',
    outputFormat: 'true',
    examples: [
      {
        input: 's = "()"',
        output: 'true',
        explanation: 'Single pair of matching parentheses.',
      },
      {
        input: 's = "()[]{}"',
        output: 'true',
        explanation: 'All types of brackets correctly matched.',
      },
      {
        input: 's = "(]"',
        output: 'false',
        explanation: 'Mismatched bracket types.',
      },
    ],
    constraints: [
      '1 <= s.length <= 10^4',
      "s consists of parentheses only '()[]{}'.",
    ],
    starterCode: {
      python: `def is_valid(s: str) -> bool:
    # Write your solution here
    return False

if __name__ == '__main__':
    print(is_valid("()[]{}"))
`,
      java: `import java.util.*;

public class Main {
    public static boolean isValid(String s) {
        // Write your solution here
        return false;
    }

    public static void main(String[] args) {
        System.out.println(isValid("()[]{}"));
    }
}
`,
      cpp: `#include <iostream>
#include <string>
#include <stack>

using namespace std;

bool isValid(string s) {
    // Write your solution here
    return false;
}

int main() {
    cout << boolalpha << isValid("()[]{}") << endl;
    return 0;
}
`,
    },
  },
];
