
Can run this in the terminal to test the application locally.

```bash
curl -X POST \
  'http://127.0.0.1:8000/api/v1/solve/' \
  -H 'Accept: */*' \
  -H 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
  -F 'puzzle=@/Users/jacobbassett/projects/courses/sudoku/backend/data/puzzles/1.jpg' \
  -o solved_29_0.jpg
```