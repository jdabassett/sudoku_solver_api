
Can run this in the terminal to test the application locally.

```bash
curl -X POST \
  'http://127.0.0.1:8000/api/v1/solve/' \
  --header 'Accept: image/jpeg' \
  --form 'puzzle=@/Users/jacobbassett/projects/courses/sudoku/OpenCV-Sudoku-Solver/data/sudokus/2.jpg' \
  -o solved_2.jpg
```