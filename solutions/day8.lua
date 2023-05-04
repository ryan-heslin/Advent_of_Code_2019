--https://stackoverflow.com/questions/10386672/reading-whole-files-in-lua
function read(file)
    local f = assert(io.open(file, "rb"))
    local content = f:read("*all")
    f:close()
    return content
end

local parse = function(file, nrow, ncol)
    file = string.gsub(file, "\n", "")
    local layer_size = nrow * ncol
    local n_digits = string.len(file)
    result = {}

    for layer = 1, n_digits - layer_size + 1, layer_size do
        this_layer = {}
        for row = 0, nrow - 1, 1 do
            --table.insert(this_layer, {})
            this_row = {}
            for col = 0, ncol - 1, 1 do
                local index = layer + (row * ncol) + col
                local digit = tonumber(string.sub(file, index, index))
                table.insert(this_row, tonumber(digit))
            end
            table.insert(this_layer, this_row)
        end
        table.insert(result, this_layer)
    end
    return result
end

local fewest_zeroes = function(data)
    local fewest = math.huge
    local index
    local found
    for i, layer in ipairs(data) do
        found = 0
        for _, row in ipairs(layer) do
            for _, el in ipairs(row) do
                found = found + ((el == 0 and 1) or 0)
            end
        end
        if found < fewest then
            index = i
            fewest = found
        end
    end
    return index
end

local ones_times_twos = function(layer)
    local ones = 0
    local twos = 0

    for _, row in ipairs(layer) do
        for _, num in ipairs(row) do
            if num == 1 then
                ones = ones + 1
            elseif num == 2 then
                twos = twos + 1
            end
        end
    end

    return ones * twos
end

local decode = function(layers, nrow, ncol)
    local transparent = 2
    local result = {}
    local replacements = { ["0"] = " ", ["1"] = "#" }
    for row = 1, nrow, 1 do
        this_row = {}
        for col = 1, ncol, 1 do
            this_row[col] = transparent
        end
        result[row] = this_row
    end

    for _, layer in ipairs(layers) do
        for row_i, row in ipairs(layer) do
            for col_i, val in ipairs(row) do
                if
                    result[row_i][col_i] == transparent
                    and val ~= transparent
                then
                    result[row_i][col_i] = replacements[tostring(val)]
                end
            end
        end
    end

    return result
end

local render = function(x)
    local result = {}
    for i, row in ipairs(x) do
        result[i] = table.concat(row, "")
    end
    return table.concat(result, "\n")
end

local file = read("inputs/day8.txt")
local nrow = 6
local ncol = 25

local layers = parse(file, nrow, ncol)
local target_layer = fewest_zeroes(layers)
local part1 = ones_times_twos(layers[target_layer])
print(part1)

local decoded = decode(layers, nrow, ncol)
print(render(decoded))
