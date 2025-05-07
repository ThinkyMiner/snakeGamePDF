
PLAYING_FIELD_OBJ = """
###IDX### obj
<<
 /FT /Btn
 /Ff 1
 /MK <<
  /BG [
   0.9 0.9 1  % Light blue background
  ]
  /BC [
   0.2 0.2 0.8  % Dark blue border
  ]
 >>
 /Border [ 0 0 1 ]
 /P 6 0 R
 /Rect [
  ###RECT###
 ]
 /Subtype /Widget
 /T (playing_field)
 /Type /Annot
>>
endobj
"""

# Update the pixel object to include a gradient color for the snake
PIXEL_OBJ = """
###IDX### obj
<<
 /FT /Btn
 /Ff 1
 /MK <<
  /BG [
   ###COLOR###  % Dynamic color for snake and food
  ]
  /BC [
   0.5 0.5 0.5  % Gray border
  ]
 >>
 /Border [ 0 0 1 ]
 /P 6 0 R
 /Rect [
  ###RECT###
 ]
 /Subtype /Widget
 /T (P_###X###_###Y###)
 /Type /Annot
>>
endobj
"""

# Update the start screen to include a welcome message with colors
PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
 /Type /Catalog
 /AcroForm <</Fields [ ###FIELD_LIST### ]>>
 /Pages 2 0 R
 /OpenAction 5 0 R
>>
endobj

2 0 obj
<<
 /Type /Pages
 /Count 1
 /Kids [6 0 R]
>>

%% Annots Page 1 (also used as overall fields list)
10 0 obj
[
 ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
6 0 obj
<<
 /Annots 10 0 R
 /Contents 3 0 R
 /CropBox [
  0.0
  0.0
  612.0
  792.0
 ]
 /MediaBox [
  0.0
  0.0
  612.0
  792.0
 ]
 /Parent 2 0 R
 /Resources <<
 >>
 /Rotate 0
 /Type /Page
>>
endobj

3 0 obj
<< >>
stream
BT
/HeBo 24 Tf  % Set font and size
0.1 0.1 0.8 rg  % Set text color to blue
100 700 Td  % Position text
(This Game is in a PDF!) Tj
ET
BT
/HeBo 18 Tf
0.2 0.6 0.2 rg  % Set text color to green
100 650 Td
(After Pressing Start tap in the box below) Tj
ET
endstream
endobj

5 0 obj
<<
 /JS 42 0 R
 /S /JavaScript
>>
endobj

42 0 obj
<< >>
stream
// ### START OF SNAKE GAME JAVASCRIPT ###
// Hacky wrapper to work with a callback instead of a string
function setInterval(cb, ms) {
	evalStr = "(" + cb.toString() + ")();";
	return app.setInterval(evalStr, ms);
}

var rand_seed = Date.now() % 1047483647;
function rand() {
	return rand_seed = rand_seed * 6807 % 1047483647;
}

var TICK_INTERVAL = 180; 
var GAME_STEP_TIME = 180; 

// Globals
var pixel_fields = [];
// var field = []; 
var score = 0;
var time_ms = 0;
var last_update = 0;
var interval = 0;
var game_over_flag = false;

// Snake
var snake_body = []; 
var snake_dx = 1;    // Initial direction: right
var snake_dy = 0;
var initial_snake_length = 3; // Starting length of the snake

// Food
var food_x = -1;
var food_y = -1;

function set_controls_visibility(state) {
	this.getField("T_input").hidden = !state;
	this.getField("B_left").hidden = !state;
	this.getField("B_right").hidden = !state;
	this.getField("B_up").hidden = !state; 
	this.getField("B_down").hidden = !state;

}

function init_snake() {
    snake_body = [];
    // Start snake in the middle, moving right
    var start_x = Math.floor(###GRID_WIDTH### / 4); // Start a bit to the left
    var start_y = Math.floor(###GRID_HEIGHT### / 2);
    for (var i = 0; i < initial_snake_length; i++) {
        // Snake grows from head to tail, so initial segments are to the left of the head
        snake_body.push({x: start_x - i, y: start_y});
    }
    snake_dx = 1; // Moving right
    snake_dy = 0;
}

function spawn_food() {
    var is_on_snake;
    var attempts = 0; 
    do {
        is_on_snake = false;
        food_x = rand() % ###GRID_WIDTH###;
        food_y = rand() % ###GRID_HEIGHT###;
        for (var i = 0; i < snake_body.length; i++) {
            if (snake_body[i].x === food_x && snake_body[i].y === food_y) {
                is_on_snake = true;
                break;
            }
        }
        attempts++;
    } while (is_on_snake && attempts < (###GRID_WIDTH### * ###GRID_HEIGHT###));
    if (is_on_snake) { // Could not place food
        game_over(); // Or handle differently
    }
}

function game_init() {
    game_over_flag = false;
	init_snake();
    spawn_food();

	// Gather references to pixel field objects
	for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		pixel_fields[x] = [];
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			pixel_fields[x][y] = this.getField("P_" + x + "_" + y);
		}
	}

	last_update = 0; // Reset time for updates
    time_ms = 0;     // Reset game time
	score = 0;
    draw_updated_score();

	// Start timer
    if (interval) { app.clearInterval(interval); } // Clear existing interval if any
	interval = setInterval(game_tick, TICK_INTERVAL);

	this.getField("B_start").hidden = true;

	set_controls_visibility(true);
}

function move_snake_and_check_collisions() {
    if (game_over_flag) return;

    var head_x = snake_body[0].x + snake_dx;
    var head_y = snake_body[0].y + snake_dy;

    if (head_x < 0 || head_x >= ###GRID_WIDTH### || head_y < 0 || head_y >= ###GRID_HEIGHT###) {
        game_over();
        return;
    }

    for (var i = 0; i < snake_body.length; i++) {
        if (head_x === snake_body[i].x && head_y === snake_body[i].y) {
            game_over();
            return;
        }
    }

    // Move snake: add new head
    snake_body.unshift({x: head_x, y: head_y});

    // Check food eaten
    if (head_x === food_x && head_y === food_y) {
        score++;
        draw_updated_score();
        spawn_food();
    } else {
        snake_body.pop();
    }
}


function game_update() {
    if (game_over_flag) return;
	if (time_ms - last_update >= GAME_STEP_TIME) {
		move_snake_and_check_collisions();
		last_update = time_ms; 
	}
}

function game_over() {
    if (game_over_flag) return; // Prevent multiple calls
    game_over_flag = true;
	app.clearInterval(interval);
	app.alert("Game over! Score: " + score + "\\nRefresh (re-open PDF) to restart.");
}


function handle_input(event) {
    if (game_over_flag) return;
    var key = event.change;
	switch (key) {
		case 'w': // Up
            if (snake_dy === 0) { 
                snake_dx = 0;
                snake_dy = -1; 
            }
			break;
		case 'a': // Left
            if (snake_dx === 0) { 
                snake_dx = -1;
                snake_dy = 0;
            }
			break;
        case 's': // Down
            if (snake_dy === 0) { 
                snake_dx = 0;
                snake_dy = 1;  
            }
			break;
		case 'd': // Right
            if (snake_dx === 0) { 
                snake_dx = 1;
                snake_dy = 0;
            }
			break;
	}
}

// Button press handlers
function press_up() { if (game_over_flag || snake_dy === 1) return; snake_dx = 0; snake_dy = -1; }
function press_left() { if (game_over_flag || snake_dx === 1) return; snake_dx = -1; snake_dy = 0; }
function press_down() { if (game_over_flag || snake_dy === -1) return; snake_dx = 0; snake_dy = 1; }
function press_right() { if (game_over_flag || snake_dx === -1) return; snake_dx = 1; snake_dy = 0; }


function draw_updated_score() {
	this.getField("T_score").value = "Score: " + score;
}

function set_pixel(x, y, state) {
	if (x < 0 || y < 0 || x >= ###GRID_WIDTH### || y >= ###GRID_HEIGHT###) {
		return;
	}
	pixel_fields[x][###GRID_HEIGHT### - 1 - y].hidden = !state;
}

function clear_field_drawing() {
    for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			set_pixel(x, y, false); // Turn all pixels off
		}
	}
}

function draw_snake() {
    for (var i = 0; i < snake_body.length; i++) {
        var segment = snake_body[i];
        set_pixel(segment.x, segment.y, true);
    }
}

function draw_food() {
    if (food_x !== -1 && food_y !== -1) { // Check if food exists
        set_pixel(food_x, food_y, true);
    }
}

function draw() {
    if (game_over_flag && score > 0) { // Optionally stop drawing or show a game over screen
        return;
    }
	clear_field_drawing(); // Clear entire board before redrawing
	draw_snake();
	draw_food();
}

function game_tick() {
	time_ms += TICK_INTERVAL; // Increment game time
	game_update(); // Handles snake movement and logic
	draw();        // Handles rendering snake and food
}

// Initial setup for when the PDF opens, before "Start Game" is pressed.
// Hide game-specific controls.
if (this.getField("T_input")) this.getField("T_input").hidden = true;
if (this.getField("B_left")) this.getField("B_left").hidden = true;
if (this.getField("B_right")) this.getField("B_right").hidden = true;
if (this.getField("B_up")) this.getField("B_up").hidden = true; // For the new up button
if (this.getField("B_down")) this.getField("B_down").hidden = true;


try { 
    app.execMenuItem("FitPage");
} catch (e) {
}
// ### END OF SNAKE GAME JAVASCRIPT ###
endstream
endobj


18 0 obj
<<
 /JS 43 0 R
 /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream
endstream
endobj

trailer
<<
 /Root 1 0 R
>>

%%EOF
"""

FONT_HELVETICA_OBJ = """
19 0 obj % Using 19 0 R for HeBo as example, ensure it doesn't clash.
<<
  /Type /Font
  /Subtype /Type1
  /BaseFont /Helvetica
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
	/AA <<
		/K <<
			/JS ###SCRIPT_IDX### R
			/S /JavaScript
		>>
	>>
	/F 4
	/FT /Tx
	/MK <<
	>>
	/MaxLen 0
	/P 6 0 R
	/Rect [
		###RECT###
	]
	/Subtype /Widget
	/T (###NAME###)
	/V (###LABEL###) % Default value
	/Type /Annot
>>
endobj
"""

STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

PX_SIZE = 15 
GRID_WIDTH = 20 
GRID_HEIGHT = 20 
GRID_OFF_X = 150
GRID_OFF_Y = 250 

fields_text = ""
field_indexes = []
obj_idx_ctr = 50 # Start object counter


def add_field(field_str_template, is_font=False): 
	global fields_text, field_indexes, obj_idx_ctr
	current_idx = obj_idx_ctr
	if is_font and "19 0" in field_str_template: 
	    pass

	fields_text += field_str_template #type: ignore
	field_indexes.append(current_idx) 
	obj_idx_ctr += 1


# Playing field outline
playing_field_template = PLAYING_FIELD_OBJ # Use a different variable name
pf_rect = f"{GRID_OFF_X} {GRID_OFF_Y} {GRID_OFF_X+GRID_WIDTH*PX_SIZE} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE}"
add_field(playing_field_template.replace("###IDX###", f"{obj_idx_ctr} 0").replace("###RECT###", pf_rect))


for x in range(GRID_WIDTH):
	for y in range(GRID_HEIGHT):
		pixel_template = PIXEL_OBJ
		pixel_rect = f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y*PX_SIZE} {GRID_OFF_X+(x+1)*PX_SIZE} {GRID_OFF_Y+(y+1)*PX_SIZE}"

		add_field(
		    pixel_template.replace("###IDX###", f"{obj_idx_ctr} 0")
		    .replace("###COLOR###", "0 0 0") 
		    .replace("###RECT###", pixel_rect)
		    .replace("###X###", str(x))
		    .replace("###Y###", str(y))
		)


def add_text(label, name, x_pos, y_pos, width, height, js_on_key): 
    global fields_text, field_indexes, obj_idx_ctr

    script_idx = obj_idx_ctr
    script_content = STREAM_OBJ.replace("###IDX###", f"{script_idx} 0").replace("###CONTENT###", js_on_key)
    add_field(script_content) 

    text_obj_idx = obj_idx_ctr
    text_content = TEXT_OBJ.replace("###IDX###", f"{text_obj_idx} 0") \
                           .replace("###SCRIPT_IDX###", f"{script_idx} 0") \
                           .replace("###LABEL###", label) \
                           .replace("###NAME###", name) \
                           .replace("###RECT###", f"{x_pos} {y_pos} {x_pos + width} {y_pos + height}")
    add_field(text_content) 


add_text("WASD for controls", "T_input", GRID_OFF_X, GRID_OFF_Y - 30, GRID_WIDTH*PX_SIZE, 30, "handle_input(event);") 
add_text("Score: 0", "T_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE + 10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 30, 100, 30, "")


# Add a start button to the PDF
START_BUTTON_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 65536  % Pushbutton
  /MK <<
    /BG [ 0.2 0.8 0.2 ]  % Green background
    /BC [ 0 0.5 0 ]  % Dark green border
    /CA (Start)  % Button label
  >>
  /AP <<
    /N ###AP_IDX### R  % Appearance stream reference
  >>
  /A <<
    /S /JavaScript
    /JS (game_init();)  % JavaScript to start the game
  >>
  /Rect [ ###RECT### ]
  /Subtype /Widget
  /T (B_start)
  /Type /Annot
>>
endobj
"""

# Add the start button to the PDF
start_button_rect = f"{GRID_OFF_X + (GRID_WIDTH * PX_SIZE) / 2 - 50} {GRID_OFF_Y + (GRID_HEIGHT * PX_SIZE) / 2 - 50} {GRID_OFF_X + (GRID_WIDTH * PX_SIZE) / 2 + 50} {GRID_OFF_Y + (GRID_HEIGHT * PX_SIZE) / 2 + 50}"
start_button = START_BUTTON_OBJ.replace("###IDX###", f"{obj_idx_ctr} 0").replace("###AP_IDX###", f"{obj_idx_ctr + 1} 0").replace("###RECT###", start_button_rect)
add_field(start_button)

START_BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 100.0 100.0 ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0 ]
  /Resources <<
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
0.2 0.8 0.2 rg  % Green fill color
0 0 100 100 re f
Q
BT
/HeBo 24 Tf
0 0 0 rg  % Black text color
25 40 Td
(Start) Tj
ET
endstream
endobj
"""

start_button_ap_stream = START_BUTTON_AP_STREAM.replace("###IDX###", f"{obj_idx_ctr} 0")
add_field(start_button_ap_stream)


js_in_template = PDF_FILE_TEMPLATE.split("42 0 obj\n<< >>\nstream\n")[1].split("\nendstream\nendobj")[0]

snake_js_final = js_in_template.replace("###GRID_WIDTH###", str(GRID_WIDTH))
snake_js_final = snake_js_final.replace("###GRID_HEIGHT###", str(GRID_HEIGHT))

pdf_parts = PDF_FILE_TEMPLATE.split(js_in_template)
filled_pdf = pdf_parts[0] + snake_js_final + pdf_parts[1]


filled_pdf = filled_pdf.replace("###FIELDS###", fields_text)
field_refs_str = " ".join([f"{i} 0 R" for i in field_indexes])
filled_pdf = filled_pdf.replace("###FIELD_LIST###", field_refs_str)

filled_pdf = filled_pdf.replace("###GRID_WIDTH###", str(GRID_WIDTH))
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", str(GRID_HEIGHT))


with open("out_snake_game.pdf", "w", encoding="latin-1") as pdffile:
    pdffile.write(filled_pdf)

print(f"Snake game PDF 'out_snake_game.pdf' generated with {obj_idx_ctr-1} objects.")
print(f"Grid: {GRID_WIDTH}x{GRID_HEIGHT}, Pixel Size: {PX_SIZE}")