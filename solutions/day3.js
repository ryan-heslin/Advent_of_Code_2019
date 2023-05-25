const fs = require('fs');

function parse(line) {
    return line.split(",").map(to_number);
}

function to_number(instr) {
    let char = instr.substring(0, 1);
    let num = Number(instr.substring(1));
    // Direction, axis, distance
    let result = [char === "D" || char === "L" ? -1 : 1,
    char == "R" || char == "L" ? 0 : 1, num]
    return result;

}

function follow(instrs) {
    let traversed = {};
    let position = [0, 0];
    let steps = 0;

    for (inst of instrs) {
        let dir = inst[0];
        let axis = inst[1];
        let distance = inst[2];
        for (let i = 0; i < distance; i++) {
            steps++;
            position[axis] += dir;
            let key = position.join(",");
            if (!(key in traversed)) {
                traversed[key] = steps
            }
        }
    }
    return traversed;
}

function solve(first, second) {
    let x = new Set(Object.keys(first));
    let y = new Set(Object.keys(second));
    let common = Array.from(x).filter((el) => y.has(el));

    let distances = common.map(manhattan);
    let combined = common.map((x) => first[x] + second[x]);
    return [Math.min(...distances), Math.min(...combined)];
}

function manhattan(coord) {
    // I felt unclean after writing this
    let arr = coord.split(",").map(Number);
    return Math.abs(arr[0]) + Math.abs(arr[1]);
}

const raw_input = fs.readFileSync('inputs/day3.txt', 'utf-8').toString().replace(/\n+$/, "").split("\n");
const lines = raw_input.map(parse);

const traversed = lines.map(follow);
const solution = solve(...traversed);
console.log(solution[0]);
console.log(solution[1]);
