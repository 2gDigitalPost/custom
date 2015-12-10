# custom
The 'custom' directory that tactic uses.

Here is a little history behind this repository for the brave programmer charged with maintaining this monster. Saying the legacy code
was written by someone who most would consider to be a bad programmer, would be a gross understatement. He-who-must-not-be-named
(I'll just refer to him as "MTM") was a terrible programmer, and the extent of the terribleness still surprises me daily. Basic
programming concepts seem unknown to him, like type casting and even string concatenation. Instead of extending a class he needed,
MTM would copy the entire class, paste it into the same file, then rename it and change whatever functions were necessary. Yes, instead
of a child class, he made a sibling class, in the tactic source code as well. Speaking of source code, most developers know not to
make changes to third-party code, because if an update is released then you have to re-insert all your changes. MTM did not understand
this. After running a diff on tactic's src directory, I found 124 files that had been modified by him. 124 files that have to be
manually changed every time southpaw releases an update. MTM would also copy and paste entire functions rather than make a module
of useful functions that would be imported. I found a function that was copied 52 times throughout the repo, 8 times within a
single file.

Anyway, this horribly unstable codebase that MTM created also used no version control system. There are many .bak files and large
sections of commented out code with no explanation or reason behind it. That is why most of this code seems to be created around
July 2015 in the initial commit. There is no commit history before that, no documentation and no unit tests. When you are required
to make a change, it will be up to you to determine what the code does (or tries to do) based on little to no context. If you have
taken my code test, then you have already been exposed to some of the stupidity that you will inevitably find in this
unmaintainable legacy code.

In my honest opinion, which has been voiced multiple times but fell on deaf ears, it is not worth fixing. The amount of technical debt
is astronomical. Resources would be much better spent on scrapping this code and developing a new system from scratch. But until that
happens, this ticking time bomb will remain in use, and must be maintained. If you are reading this, then you were deemed worthy of
this task. But for the sake of your own sanity, try to convince them to hire more developers and build a new system. The long-term
benefit would far outweigh the cost, and would be a much more pleasant experience for everyone involved.
