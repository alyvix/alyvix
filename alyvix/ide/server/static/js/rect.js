
class RectManager{
    
    constructor(foo) {
              
        this.mouse_is_on_left_border = false;
        this.mouse_is_on_right_border = false;
        this.mouse_is_on_top_border = false;
        this.mouse_is_on_bottom_border = false;

        this.mouse_is_on_left_up_corner = false;
        this.mouse_is_on_right_up_corner = false;
        this.mouse_is_on_right_bottom_corner = false;
        this.mouse_is_on_left_bottom_corner = false;

        this.mouse_is_on_left_border_roi = false;
        this.mouse_is_on_right_border_roi = false;
        this.mouse_is_on_top_border_roi = false;
        this.mouse_is_on_bottom_border_roi = false;

        this.mouse_is_on_left_up_corner_roi = false;
        this.mouse_is_on_right_up_corner_roi = false;
        this.mouse_is_on_right_bottom_corner_roi = false;
        this.mouse_is_on_left_bottom_corner_roi = false;
        
        this.drag_border = false;
        
        this.mouse_lbutton_pressed = false;
        this.mouse_rbutton_pressed = false;
        this.key_ctrl_pressed = false;
        
        this.show_autocontoured_rects = false;
        
        this.old_w = 0;
        this.old_h = 0;
        this.old_x = 0;
        this.old_y = 0;
        this.old_roi_w = 0;
        this.old_roi_h = 0;
        this.old_roi_x = 0;
        this.old_roi_y = 0;
        
        this.position_offset_x = 0;
        this.position_offset_y = 0;
        
        this.mouse_is_on_border = null;
        this.border_index = null;
        this.mouse_is_inside_rectangle = null;
        this.move_index = null;
        
        this.rectangles = null;
        
        this.click_position_x = null;
        this.click_position_y = null;
        
        this.capturing_rect = false;
        
        this.group = 0;
        
        this.main_g0_created = false;
        this.main_g1_created = false;
        this.main_g2_created = false;
        
        this.g0_elements_cnt = 0;
        this.g1_elements_cnt = 0;
        this.g2_elements_cnt = 0;
        
        this.last_mouse_event = null;
        
        this.deleted_rects = [];
        
        this.autocontoured_rects = [];
        
        this.intent = {"type":"capturing", "features":{}}
        
        
    }

    set_intent(intent)
    {
        this.intent = intent;
    }
    
    set_group(group){
    
        this.group = group;
    }
    
    set_rectangles(rectangles)
    {
        this.rectangles = rectangles;
    }
    
    /*set_selected(index)
    {
        this.selected = index;
    }*/
    
    get_rectangles()
    {
        return this.rectangles;
    }
    
    get_autocontoured_rects()
    {
        return this.autocontoured_rects;
    }
    
    keydown(e)
    {   

        
        if (e.key == " " && this.capturing_rect == false && this.show_autocontoured_rects == false){ 
            this.show_autocontoured_rects = true
            draw(this.last_mouse_event)
        }
            
        else if (e.key == " " && this.capturing_rect == false && this.show_autocontoured_rects == true){
            this.show_autocontoured_rects = false
            draw(this.last_mouse_event)
        }
        
        if (e.key == "Control") this.key_ctrl_pressed = true;
        
        if (e.key == "i") init_rect_type(this.rectangles[this.rectangles.length-1]);
        if (e.key == "g")
        {
            console.log(get_rect_type(this.rectangles[this.rectangles.length-1]));
            
        }
        if (e.key == "s") set_rect_type("box", this.rectangles[this.rectangles.length-1]);
        if (e.key == "d") set_rect_type("window", this.rectangles[this.rectangles.length-1]);
        if (e.key == "f") set_rect_type("button", this.rectangles[this.rectangles.length-1]);
        
        if (this.key_ctrl_pressed == true && e.key == "z")
        {
            if(this.intent["type"]==="set_interaction_point")
            {
                var interaction_dict = {
                    "dx": 0,
                    "dy": 0,
                };
                      
                this.rectangles[selected_box].mouse["features"]["point"] = interaction_dict;
                draw(this.last_mouse_event);
            }
            else if(boxes.length > 0)
            {
                var box = boxes[boxes.length-1];
                
                if (box.group == 0)
                {
                    if (box.is_main) this.main_g0_created = false;
                    
                    this.g0_elements_cnt -= 1;
                    
                    this.group = 0;
                }
                else if (box.group == 1)
                {
                    if (box.is_main) this.main_g1_created = false;
                    
                    this.g1_elements_cnt -= 1;
                    
                    this.group = 1;
                }
                else if (box.group == 2)
                {
                    if (box.is_main) this.main_g2_created = false;
                    
                    this.g2_elements_cnt -= 1;
                    
                    this.group = 2;
                }
                
                this.deleted_rects.push(boxes[boxes.length-1]);
                boxes.splice(boxes.length-1, 1) ;
                draw(this.last_mouse_event);
            }
        }
        
        if (this.key_ctrl_pressed == true && e.key == "y")
        {
            if(this.deleted_rects.length > 0)
            {
                var box = this.deleted_rects[this.deleted_rects.length-1];
                
                if (box.group == 0)
                {
                    if (box.is_main) this.main_g0_created = true;
                    
                    this.g0_elements_cnt += 1;
                }
                else if (box.group == 1)
                {
                    if (box.is_main) this.main_g1_created = true;
                    
                    this.g1_elements_cnt += 1;
                }
                else if (box.group == 2)
                {
                    if (box.is_main) this.main_g2_created = true;
                    
                    this.g2_elements_cnt += 1;
                }
                
                if(box.is_main)
                {
                    if (box.group == 0) this.main_g0_created = true;
                    else if (box.group == 1) this.main_g1_created = true;
                    else if (box.group == 2) this.main_g2_created = true;
                }
                
                boxes.push(this.deleted_rects[this.deleted_rects.length-1]);
                this.deleted_rects.splice(this.deleted_rects.length-1, 1) ;
                draw(this.last_mouse_event);
            }
        }
        
        if ((e.keyCode === 27 || (e.key == "o" && this.key_ctrl_pressed == true)) && ide) {  //esc pressed or ctrl-o
            console.log("close and go back to editor");
            save();
        }
        
        if((e.key == "o" && this.key_ctrl_pressed == true) || e.keyCode === 27 || e.keyCode === 13){
        
            e.preventDefault();
            /*var resp = null;
            var sendData = function() {
                $.post('create_thumbnail', {
                    rect_list: boxes
                  }, function(response) {
                    resp = response;
                  });
                }
            sendData();*/
            
            //dicts = boxes;
            //dicts.push({"background_img":background_base64_string});
            
            var boxes_g0 = [];
            var boxes_g1 = [];
            var boxes_g2 = [];
            
            for (var i=0; i<boxes.length; i++)
            {
                if(boxes[i].group == 0) boxes_g0.push(boxes[i]);
                
                if(boxes[i].group == 1) boxes_g1.push(boxes[i]);
                
                if(boxes[i].group == 2) boxes_g2.push(boxes[i]);
            }
            
            boxes = [];
            
            boxes = boxes.concat(boxes_g0, boxes_g1, boxes_g2);
            
            this.rectangles = boxes;
            
            /*if (boxes.length == 0)
            {
                $.ajax({
                    url: "/cancel_event",
                    type: "GET"
                });
                return;
            }*/
            
     
            
            var jsonData = JSON.stringify({box_list:boxes, background: background_base64_string});
            
            this.deleted_rects = [];
             
            this.intent = {"type":"capturing", "features":{}};
            
            $.ajax({
                url: "/create_thumbnail",
                type: "POST",
                data: jsonData,
                contentType: "application/json; charset=utf-8",
                success: function(dat) { console.log(dat); update_thumbnails(dat); }
            });
        
        }
        
        if (e.key == "1" || e.key == "2" || e.key == "3")
        {
            if(this.intent["type"] == "set_interaction_point") return;
            if(e.key == "1") this.group = 0;
            
            if(e.key == "2") this.group = 1;
            
            if(e.key == "3") this.group = 2;
            
            draw(this.last_mouse_event);
        }
        
        if (e.key == "ArrowUp")
        {
            if(boxes.length > 0)
            {
                boxes[boxes.length-1].roi_unlimited_up = true;
                draw(this.last_mouse_event);
            }
        }
        
        if (e.key == "ArrowLeft")
        {
            if(boxes.length > 0)
            {
                boxes[boxes.length-1].roi_unlimited_left = true;
                draw(this.last_mouse_event);
            }
        }
        
        if (e.key == "ArrowRight")
        {
            if(boxes.length > 0)
            {
                boxes[boxes.length-1].roi_unlimited_right = true;
                draw(this.last_mouse_event);
            }
        }
        
        if (e.key == "ArrowDown")
        {
            if(boxes.length > 0)
            {
                boxes[boxes.length-1].roi_unlimited_down = true;
                draw(this.last_mouse_event);
            }
        }

    }
    
    keyup(e)
    {   
        if (e.key == "Control") this.key_ctrl_pressed = false;
    }
    
    mousedown(e) // 1 for left, 2 for middle, 3 for right
    {
        this.mousemove(this.last_mouse_event, boxes); //draw(this.last_mouse_event);
        
        if(e.which==1){
            
            if(this.intent["type"] === "set_interaction_point")
            {
                var interaction_dict = {
                        "dx": parseInt(e.clientX),
                        "dy": parseInt(e.clientY),
                      };
                      
                this.rectangles[selected_box].mouse["features"]["point"] = interaction_dict;
            }
            
            else if(this.show_autocontoured_rects == false) 
            {   
                this.mouse_lbutton_pressed = true;

                this.click_position_x = parseInt(e.clientX);
                this.click_position_y = parseInt(e.clientY);

                if(this.mouse_is_on_border == null && this.mouse_is_inside_rectangle == null){
                    this.capturing_rect = true;

                }
                else if (this.mouse_is_on_border != null){
                    this.border_index = this.mouse_is_on_border;
                    this.drag_border = true;
                    
                    var rect = boxes[this.border_index];
                    
                    this.old_h = rect.h;
                    this.old_w = rect.w;
                    this.old_x = rect.x;
                    this.old_y  = rect.y;

                    this.old_roi_h = rect.roi_h;
                    this.old_roi_w = rect.roi_w;
                    this.old_roi_x = rect.roi_x;
                    this.old_roi_y = rect.roi_y;
                }
                else if (this.mouse_is_inside_rectangle != null && this.key_ctrl_pressed == false)
                {
                    this.move_index = this.mouse_is_inside_rectangle;
                    
            
                    var rect = boxes[this.move_index];
                    
                    this.position_offset_x = this.click_position_x - rect.x;
                    this.position_offset_y = this.click_position_y - rect.y;
                }
                else if (this.mouse_is_inside_rectangle != null && this.key_ctrl_pressed == true)
                {
                    var inside_index = this.mouse_is_inside_rectangle;
                    
            
                    var rect = boxes[inside_index];
                    this.restore_roi(rect);

                }
            }                

            
        }
        else if(e.which==3){
            
            if (this.intent["type"] === "set_interaction_point") return;

            this.mouse_rbutton_pressed = true;
            
            if(this.mouse_is_on_border != null && this.show_autocontoured_rects == false)
            {
                var rect = boxes[this.mouse_is_on_border];
                
                if (this.mouse_is_on_left_border_roi == true) rect.roi_unlimited_left = true;
                    
                if (this.mouse_is_on_right_border_roi == true) rect.roi_unlimited_right = true;
                    
                if (this.mouse_is_on_top_border_roi == true) rect.roi_unlimited_up = true;
                    
                if (this.mouse_is_on_bottom_border_roi == true) rect.roi_unlimited_down = true;
                draw();
            }
            else if (this.mouse_is_inside_rectangle != null && this.key_ctrl_pressed == true)
            {
                var inside_index = this.mouse_is_inside_rectangle;
                
                var box = boxes[inside_index];
                
                if (box.group == 0)
                {
                    if (box.is_main)
                    {
                        if (this.g0_elements_cnt > 1) return;
                        
                        this.main_g0_created = false;
                    }
                    
                    this.g0_elements_cnt -= 1;
                    
                    this.group = 0;
                }
                else if (box.group == 1)
                {
                    if (box.is_main)
                    {
                        if (this.g1_elements_cnt > 1) return;
                        
                        this.main_g1_created = false;
                    }
                    
                    this.g1_elements_cnt -= 1;
                    
                    this.group = 1;
                }
                else if (box.group == 2)
                {
                    if (box.is_main)
                    {
                        if (this.g2_elements_cnt > 1) return;
                        
                        this.main_g2_created = false;
                    }
                    
                    this.g2_elements_cnt -= 1;
                    
                    this.group = 2;
                }

                boxes.splice(inside_index, 1);

            }
            else if (this.key_ctrl_pressed == false){
                                
                this.add_rect_autocontoured(this.last_mouse_event);
            }
        }

        draw(this.last_mouse_event);
        console.log(e.which + " down");
    }
    
    mouseup(e)
    {
        if(this.show_autocontoured_rects == false)
        {
            //draw();
            if(e.which==1){
                this.mouse_lbutton_pressed = false;
                        
                if(this.capturing_rect == true){
                    this.capturing_rect = false;
                    this.deleted_rects = [];
                    this.add_rect(e);
                    draw(null);
                    
                }
                 else if (this.drag_border == true){
                    var rect = this.rectangles[this.border_index];
                    this.drag_border = false;
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;
                    this.mouse_is_on_border = null;
                    this.border_index = null;
                    
                    if (rect.type === "R")
                    {
                        if (rect.rect_type == null)
                        {
                            //this is for ide only first time object is edited
                            rect.rect_type = get_rect_type(rect);
                        }
                        
                        //alert(rect.rect_type);
                        if (rect.rect_type === "box") set_rect_type("box", rect);
                        
                        if (rect.rect_type === "window") set_rect_type("window", rect);
                        
                        if (rect.rect_type === "button") set_rect_type("button", rect);
                    }
                 }
                 else if(this.move_index != null)
                 {
                     this.move_index = null;
                 }
            }
            else if(e.which==3){
                this.mouse_rbutton_pressed = false;
            }
        }
        
        draw(this.last_mouse_event);
        console.log(e.which + " up");
    }
    
    mousemove(e, rectangles)
    {
        //var box = boxes[i];
        //ctx.strokeRect(box.x, box.y, box.w, box.h);
        
        this.last_mouse_event = e;
        
        this.mouse_is_on_border = null;
        this.mouse_is_inside_rectangle = null;

        if (this.capturing_rect == false && this.drag_border == false && this.move_index == null /*&& this.show_autocontoured_rects == false*/ && this.intent["type"] != "set_interaction_point"){
            for(i=0; i<this.rectangles.length; i++)
            {
                var rect = this.rectangles[i];
                
                if (this.is_mouse_inside_rect(e, rect) && this.mouse_is_on_border == null)
                {
                    this.mouse_is_inside_rectangle = i;
                    $("#myCanvas").css({ cursor: "move" });  
                }
                else if (this.is_mouse_on_left_border_roi(e, rect) && this.is_mouse_on_top_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_left_up_corner_roi = true;

                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;



                    this.mouse_is_on_border = i;
                    $("#myCanvas").css({ cursor: "nwse-resize" }); 

                }
                else if (this.is_mouse_on_right_border_roi(e, rect) && this.is_mouse_on_top_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_up_corner_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;

                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;


                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nesw-resize" }); 
                }
                else if (this.is_mouse_on_right_border_roi(e, rect) && this.is_mouse_on_bottom_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_bottom_corner_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;

                    this.mouse_is_on_left_bottom_corner_roi = false;

                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nwse-resize" }); 
                    
                }
                else if (this.is_mouse_on_left_border_roi(e, rect) && this.is_mouse_on_bottom_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_left_bottom_corner_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nesw-resize" }); 
                }

                else if (this.is_mouse_on_left_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_left_border_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "ew-resize" }); 
                   
                }
                                    
                else if (this.is_mouse_on_top_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_top_border_roi = true;
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;

                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "ns-resize" }); 
                }
                else if (this.is_mouse_on_right_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_border_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;

                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                     $("#myCanvas").css({ cursor: "ew-resize" }); 
                }
                else if (this.is_mouse_on_bottom_border_roi(e, rect) && rect.is_main == false && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_bottom_border_roi = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "ns-resize" }); 
                }
                else if (this.is_mouse_on_left_border(e, rect) && this.is_mouse_on_top_border(e, rect) && this.show_autocontoured_rects == false){
                    this.mouse_is_on_left_up_corner = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nwse-resize" }); 
                    
                }
                
                else if (this.is_mouse_on_right_border(e, rect) && this.is_mouse_on_top_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_up_corner = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;

                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nesw-resize" }); 
                    
                }
                
                else if (this.is_mouse_on_right_border(e, rect) && this.is_mouse_on_bottom_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_bottom_corner = true;
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;

                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nwse-resize" }); 
                }

                else if (this.is_mouse_on_left_border(e, rect) && this.is_mouse_on_bottom_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_left_bottom_corner = true;
                    
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "nesw-resize" });
                }

                else if (this.is_mouse_on_left_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_left_border = true;
                    
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "ew-resize" });
                }
                         
                else if (this.is_mouse_on_top_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_top_border = true;
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;

                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: " ns-resize" });
                }
      
                else if (this.is_mouse_on_right_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_right_border = true;
                    
                    this.mouse_is_on_left_border = false;

                    this.mouse_is_on_top_border = false;
                    this.mouse_is_on_bottom_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: "ew-resize" });
                    //#QApplication.setOverrideCursor(Qt.SizeHorCursor)
                }
         
                else if (this.is_mouse_on_bottom_border(e, rect) && this.show_autocontoured_rects == false)
                {
                    this.mouse_is_on_bottom_border = true;
                    this.mouse_is_on_left_border = false;
                    this.mouse_is_on_right_border = false;
                    this.mouse_is_on_top_border = false;

                    this.mouse_is_on_left_up_corner = false;
                    this.mouse_is_on_right_up_corner = false;
                    this.mouse_is_on_right_bottom_corner = false;
                    this.mouse_is_on_left_bottom_corner = false;

                    this.mouse_is_on_left_border_roi = false;
                    this.mouse_is_on_right_border_roi = false;
                    this.mouse_is_on_top_border_roi = false;
                    this.mouse_is_on_bottom_border_roi = false;

                    this.mouse_is_on_left_up_corner_roi = false;
                    this.mouse_is_on_right_up_corner_roi = false;
                    this.mouse_is_on_right_bottom_corner_roi = false;
                    this.mouse_is_on_left_bottom_corner_roi = false;
                    
                    this.mouse_is_on_border = i;
                    //mouse_on_border = True
                    $("#myCanvas").css({ cursor: " ns-resize" });

                }
            }
        }
        else if (this.drag_border == true)
        {
            this.update_border(e);
        }
        else if (this.move_index != null)
        {
            this.update_position(e);
        }
        
        if (this.mouse_is_on_border == null && this.mouse_is_inside_rectangle == null)
        {
            $("#myCanvas").css({ cursor: "crosshair" });    
        }

        
        
        
    }
    
    
    draw_capturing_rect(e)
    {
        if (rect.h > 16 && rect.w > 16){
            return 6;
        }
        else if (rect.h > 12 && rect.w > 12){
            return 4;
        }
        else if (rect.h > 8 && rect.w > 8){
            return 2;
        }
        else if (rect.h > 4 && rect.w > 4){
            return 1;
        }
        else {
            return 0;
        }
                
    }
    
    restore_roi(rect){
        var hw_factor = 0;
                                    
        if (rect.h < rect.w) hw_factor = rect.h;
        else hw_factor = rect.w;
            
            
        var sc_factor = 0;
                            
        if (screen_h < screen_w) sc_factor = screen_h;
        else sc_factor = screen_w;
            
        var percentage_screen_w = Math.ceil(0.0125 * sc_factor);
        var percentage_screen_h = Math.ceil(0.0125 * sc_factor);
        var percentage_object_w = Math.ceil(0.2 * hw_factor);
        var percentage_object_h = Math.ceil(0.2 * hw_factor);
        
        var roi_h_full = percentage_screen_h + percentage_object_h + rect.h;
        var roi_w_full = percentage_screen_w + percentage_object_w + rect.w;
        

        var roi_w_half = Math.ceil((roi_w_full - rect.w)/2);
        var roi_h_half = Math.ceil((roi_h_full - rect.h)/2);


        var roi_x = rect.x - roi_w_half;
        var roi_y = rect.y - roi_h_half;
        var roi_w = rect.w + (roi_w_half*2);
        var roi_h = rect.h + (roi_h_half*2);
        
        rect.roi_x = roi_x;
        rect.roi_y = roi_y;
        rect.roi_w = roi_w;
        rect.roi_h = roi_h;
        rect.roi_unlimited_left = false;
        rect.roi_unlimited_up = false;
        rect.roi_unlimited_right = false;
        rect.roi_unlimited_down = false;
        
            
    }
    
    add_rect(e)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var x = this.click_position_x;
        var y = this.click_position_y;
        
        var w = mouse_x - x;
        var h = mouse_y - y;

        if ((w >= 3 || w <= -3) && (h >= 3 || h <= -3)){

            if (w < 0 && h < 0){

                x = x + w;
                y = y + h;
                w = -w;
                h = -h;
            }

            else if (w < 0 && h > 0){

                x = x + w;
                w = -w;
            }

            else if (w > 0 && h < 0){

                y = y + h;
                h = -h;
            }

            if (w < 0) w = -w;
            
            if (h < 0) h = -h;
        
            
            /*var height_factor = 0.22;
            
            if (h > 40) height_factor = 0.18;
                        
            if (h > 90) height_factor = 0.11;
                
            if (h > 130) height_factor = 0.08;
                
            if (h > 300) height_factor = 0.06;
                
            if (h > 600) height_factor = 0.03;
                
                
            var width_factor = 0.22;
            
            if (w > 40) width_factor = 0.18;
                        
            if (w > 90) width_factor = 0.11;
                
            if (w > 130) width_factor = 0.08;
                
            if (w > 300) width_factor = 0.06;
                
            if (w > 600) width_factor = 0.03;
            
                
            var min_height = Math.ceil(h-(h*height_factor));
            var max_height = Math.ceil(h+(h*height_factor));
            var min_width = Math.ceil(w-(w*width_factor));
            var max_width = Math.ceil(w+(w*width_factor));
            
            
            var height_tolerance = Math.ceil(h*height_factor);
            
            var width_tolerance = Math.ceil(w*width_factor);*/

            var box = new Box(x, y, w, h, 0, 0, 0, 0);
            //box.roi_unlimited_up = true;
            
            this.restore_roi(box);
            
            if(this.group == 0)
            {
                if (this.g0_elements_cnt >= 5) return;
                
                box.group = 0;
                
                if (this.main_g0_created == false)
                {
                    this.main_g0_created = true;
                    box.is_main = true;
                }
                
                this.g0_elements_cnt += 1;
                if (this.g0_elements_cnt >= 5 && this.g1_elements_cnt < 5) this.group = 1;
            }
            else if (this.group == 1)
            {
                if (this.g1_elements_cnt >= 5) return;
                
                box.group = 1;
                
                if (this.main_g1_created == false)
                {
                    this.main_g1_created = true;
                    box.is_main = true;
                }
                
                this.g1_elements_cnt += 1;
                if (this.g1_elements_cnt >= 5 && this.g2_elements_cnt < 5) this.group = 2;
            }
            else if (this.group == 2)
            {
                if (this.g2_elements_cnt >= 5) return;
                
                box.group = 2;
                
                if (this.main_g2_created == false)
                {
                    this.main_g2_created = true;
                    box.is_main = true;
                }
                
                this.g2_elements_cnt += 1;
                if (this.g2_elements_cnt >= 5 && this.g0_elements_cnt < 5) this.group = 0;
            }
            
            
            
            boxes.push(box);
            
            last_element = box;
            
            //self._main_rect_finder = rect_finder

            //self.__deleted_rects = []
            
        }
    }
    
    add_rect_autocontoured(e)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var selected_rects = [];
        
        for(i=0; i<this.autocontoured_rects.length; i++)
        {
                        
            var x = this.autocontoured_rects[i].x;
            var y = this.autocontoured_rects[i].y;
            var w = this.autocontoured_rects[i].w;
            var h = this.autocontoured_rects[i].h;
            
            if (mouse_x > x &&
                    mouse_x < w + x &&
                    mouse_y > y &&
                    mouse_y < h + y)
                {
                                        
                    selected_rects.push(this.autocontoured_rects[i]);
                }

        }
        
        selected_rects.sort(function(a, b){return (a.w*a.h)-(b.w*b.h)});
        
        var box = new Box(selected_rects[0].x, selected_rects[0].y, selected_rects[0].w, selected_rects[0].h, 0, 0, 0, 0);
            
        //box.roi_unlimited_up = true;
        
        this.restore_roi(box);
        
        if(this.group == 0)
        {
            if (this.g0_elements_cnt >= 5){
                //if (this.g2_elements_cnt < 5) this.group = 2;
                return;
            }
            
            box.group = 0;
            
            if (this.main_g0_created == false)
            {
                this.main_g0_created = true;
                box.is_main = true;
            }
            
            this.g0_elements_cnt += 1;
            
            if (this.g0_elements_cnt >= 5 && this.g1_elements_cnt < 5) this.group = 1;

        }
        else if (this.group == 1)
        {
            if (this.g1_elements_cnt >= 5) {
                //if (this.g0_elements_cnt < 5) this.group = 0;
                return;
            }
            
            box.group = 1;
            
            if (this.main_g1_created == false)
            {
                this.main_g1_created = true;
                box.is_main = true;
            }
            
            this.g1_elements_cnt += 1;
            if (this.g1_elements_cnt >= 5 && this.g2_elements_cnt < 5) this.group = 2;
        }
        else if (this.group == 2)
        {
            if (this.g2_elements_cnt >= 5){
                //if (this.g1_elements_cnt < 5) this.group = 1;
                return;
            }
            
            box.group = 2;
            
            if (this.main_g2_created == false)
            {
                this.main_g2_created = true;
                box.is_main = true;
            }
            
            this.g2_elements_cnt += 1;
            if (this.g2_elements_cnt >= 5 && this.g0_elements_cnt < 5) this.group = 0;
        }
        
        
        
        boxes.push(box);
        
        last_element = box;

    }
    
    draw_autocontoured_rect(crx, rect){

        ctx.globalAlpha=0.5;

        ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
        ctx.globalAlpha=1;
        ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
    }
        
    draw_rect(ctx, rect, index){
    
        
        var roi_x =  rect.roi_x;
        var roi_y =  rect.roi_y;
        var roi_w =  rect.roi_w;
        var roi_h =  rect.roi_h;

        if  (rect.roi_unlimited_up == true){
            roi_y = 0;
            roi_h =  rect.roi_y + roi_h;
        }

        if  (rect.roi_unlimited_down == true){
            if (rect.roi_unlimited_up == true) roi_h = screen_h-1;
            else roi_h = screen_h - ( rect.roi_y + 1);
        }

        if (rect.roi_unlimited_left == true){
            roi_x = 0;
            roi_w = rect.roi_x + roi_w;
        }

        if (rect.roi_unlimited_right == true){
            if (rect.roi_unlimited_left == true) roi_w = screen_w -1;
            else roi_w = screen_w - ( rect.roi_x + 1);
        }
        
        if (rect.type === "R" && selected_box == index && ttWIndow_isOpen == true)
        {
            var rect_center_x = rect.x + parseInt(rect.w/2);
            var rect_center_y = rect.y + parseInt(rect.h/2);
            
            var min_height = rect.features["R"]["height"]["min"];
            var max_height = rect.features["R"]["height"]["max"];
            
            var min_width = rect.features["R"]["width"]["min"];
            var max_width = rect.features["R"]["width"]["max"];
            
            if (min_width < 0) min_width = 0;
            
            if (min_height < 0) min_height = 0;
            
            
            var x_min =  rect_center_x - parseInt(min_width/2);
            var y_min = rect_center_y - parseInt(min_height/2);
            
            var x_max =  rect_center_x - parseInt(max_width/2);
            var y_max = rect_center_y - parseInt(max_height/2);
            
            if(rect.is_main == false)
            {
                if (x_max < roi_x || max_width == roi_w) x_max = roi_x;
                
                if (y_max < roi_y || max_height == roi_h) y_max = roi_y;
                
                if (x_max + max_width > roi_x + roi_w) max_width = max_width - ((x_max + max_width) - (roi_x + roi_w));
                
                if (y_max + max_height > roi_y + roi_h) max_height = max_height - ((y_max + max_height) - (roi_y + roi_h));
                
                ctx.globalAlpha=0.2;
                ctx.fillRect(roi_x, roi_y, roi_w, roi_h);
                ctx.globalAlpha=1;
                ctx.strokeRect(roi_x, roi_y, roi_w, roi_h);
                
            }
            else
            {
                if (x_max < 0 || max_width == screen_w) x_max = 0;
                
                if (y_max < 0 || max_height == screen_h) y_max = 0;
                
                if (x_max + max_width > screen_w) max_width = max_width - ((x_max + max_width) - (screen_w));
                
                if (y_max + max_height > screen_h) max_height = max_height - ((y_max + max_height) - (screen_h));
            }
            
            if(rect.is_main == false) ctx.globalAlpha=0.3;
            else  ctx.globalAlpha=0.5;
            ctx.beginPath();
            ctx.rect(x_max, y_max, max_width, max_height);
            
            ctx.moveTo(x_min, y_min);
            ctx.rect(x_min, y_min, min_width, min_height);
            
            ctx.fill('evenodd');

            ctx.globalAlpha=1;
            
            
            ctx.strokeRect(x_min, y_min, min_width, min_height);
            if(rect.is_main == false) ctx.strokeRect(x_max, y_max, max_width, max_height);
            else ctx.strokeRect(x_max, y_max, max_width-1, max_height-1);
            
        }
        else
        {
            if(rect.is_main == false)
            {
                
                ctx.globalAlpha=0.2;
                ctx.fillRect(roi_x, roi_y, roi_w, roi_h);
                ctx.globalAlpha=1;
                ctx.strokeRect(roi_x, roi_y, roi_w, roi_h);
            }
            
            if(rect.is_main == false) ctx.globalAlpha=0.3;
            else  ctx.globalAlpha=0.5;

            ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
            ctx.globalAlpha=1;
            ctx.strokeRect(rect.x, rect.y, rect.w, rect.h);
        }

        
        var mouse_type = rect.mouse['type'];
        var mouse_features = rect.mouse['features'];
        var mouse_point = mouse_features["point"];
            
        
        if (mouse_type === "click" || mouse_type ===  "move" || mouse_type ===  "scroll" || mouse_type ===  "release" || mouse_type ===  "hold")
        {
            var rect_center_x = rect.x + parseInt(rect.w/2);
            var rect_center_y = rect.y + parseInt(rect.h/2);
            
            var lineTo_x = 0;
            var lineTo_y = 0;
            
                            
            var arc_r = 4;

            if(mouse_point["dx"] != 0 || mouse_point["dy"] != 0)
            {
                
                lineTo_x = mouse_point["dx"];
                lineTo_y = mouse_point["dy"];
            }
            else
            {

                
                lineTo_x = rect_center_x;
                lineTo_y = rect_center_y;

            }
            
            if(rect.group == 0)
            {
                ctx.strokeStyle = '#ff0000';
                ctx.fillStyle = '#ff0000'; 
            } 
            else if (rect.group == 1)
            {
                ctx.strokeStyle = '#009500';
                ctx.fillStyle = '#009500';
            }
            else if (rect.group == 2)
            {
                ctx.strokeStyle = '#0000ff';
                ctx.fillStyle = '#0000ff';
            } 
            
            ctx.beginPath();
            ctx.moveTo(rect_center_x, rect_center_y);
            ctx.lineTo(lineTo_x, lineTo_y);
            ctx.stroke(); 
            ctx.closePath();
            
            ctx.beginPath();
            ctx.arc(lineTo_x, lineTo_y, arc_r, 0, 2 * Math.PI);
            ctx.fill(); 
            ctx.closePath();
        }
        else
        {
        }
        
    
    }
    
    calc_threshold_inside(rect)
    {
        if (rect.h > 16 && rect.w > 16){
            return 6;
        }
        else if (rect.h > 12 && rect.w > 12){
            return 4;
        }
        else if (rect.h > 8 && rect.w > 8){
            return 2;
        }
        else if (rect.h > 4 && rect.w > 4){
            return 1;
        }
        else {
            return 0;
        }
                
    }
    
    calc_threshold_border_roi(rect)
    {
        if (rect.roi_h > 16 && rect.roi_w > 16){
            return 8;
        }
        else if (rect.roi_h > 12 && rect.roi_w > 12){
            return 6;
        }
        else if (rect.roi_h > 8 && rect.roi_w > 8){
            return 4;
        }
        else if (rect.roi_h > 4 && rect.roi_w > 4){
            return 2;
        }
        else {
            return 1;
        }
    }
    
    calc_threshold_border(rect)
    {
        if (rect.h > 16 && rect.w > 16){
            return 8;
        }
        else if (rect.h > 12 && rect.w > 12){
            return 6;
        }
        else if (rect.h > 8 && rect.w > 8){
            return 4;
        }
        else if (rect.h > 4 && rect.w > 4){
            return 2;
        }
        else{
            return 1;
        }
    }
    
    is_mouse_inside_rect(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);

        var threshold = this.calc_threshold_inside(rect);
        
        if (mouse_x > rect.x + threshold &&
                mouse_x < rect.w + rect.x - threshold &&
                mouse_y > rect.y + threshold &&
                mouse_y < rect.h + rect.y - threshold){
            return true;
        }

        else {
            return false;
        }
    }
    
    is_mouse_on_left_border(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border(rect);
        
        if (mouse_x > rect.x - threshold &&
                mouse_x < rect.x + threshold &&
                mouse_y > rect.y - threshold &&
                mouse_y < rect.h + rect.y + threshold){
            return true;
        }
        else{
            return false;
        }
    }
    
    is_mouse_on_top_border(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border(rect);
        
        if (mouse_x > rect.x - threshold &&
                mouse_x < rect.x + rect.w + threshold &&
                mouse_y > rect.y - threshold &&
                mouse_y < rect.y + threshold){
            return true;
        }
        else{
            return false;
        }
    }
    
    is_mouse_on_right_border(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border(rect);
        
        if (mouse_x > rect.x + rect.w - threshold &&
                mouse_x < rect.x + rect.w + threshold &&
                mouse_y > rect.y -  threshold &&
                mouse_y < rect.h + rect.y +  threshold ){
            return true;
        }
        else{
            return false;
        }
    }
    
    is_mouse_on_bottom_border(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border(rect);
        
        if (mouse_x > rect.x - threshold &&
                mouse_x < rect.x + rect.w + threshold &&
                mouse_y > rect.y + rect.h - threshold &&
                mouse_y < rect.y + rect.h + threshold){
                    
            return true;
        }
        else{
            return false;
        }
    }
    
    is_mouse_on_left_up_corner(rect)
    {
    }
    
    is_mouse_on_right_up_corner(rect)
    {
    }
    
    is_mouse_on_right_bottom_corner(rect)
    {
    }
    
    is_mouse_on_left_bottom_corner(rect)
    {
    }
    
    is_mouse_on_left_border_roi(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border_roi(rect);
    
        if (rect.x == 0 && rect.w == 0 && rect.y == 0 && rect.h == 0){
            return false;
        }
        
        if (rect.roi_unlimited_left == true ){
            return false;
        }
        else if (mouse_x > rect.roi_x - threshold &&
                mouse_x < rect.roi_x + threshold &&
                mouse_y > rect.roi_y - threshold &&
                mouse_y < rect.roi_h + rect.roi_y + threshold){
            return true;
        }
        else if (rect.roi_unlimited_up == true  &&
                mouse_x > rect.roi_x - threshold &&
                mouse_x < rect.roi_x + threshold &&
                
                mouse_y < rect.roi_y + rect.roi_h + threshold)
                {
                    console.log("tt");
                    return true;
                }
                
        else if (rect.roi_unlimited_down == true  &&
                mouse_x > rect.roi_x - threshold &&
                mouse_x < rect.roi_x + threshold &&
                
                mouse_y > rect.roi_y - threshold)
                {
                    console.log("tut");
                    return true;
                }
        else {
            return false;
        }
    }
    
    is_mouse_on_top_border_roi(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border_roi(rect);
    
        if (rect.x == 0 && rect.w == 0 && rect.y == 0 && rect.h == 0){
            return false;
        }
        
    
        if (rect.roi_unlimited_up == true ) return false;
        
        else if (mouse_x > rect.roi_x - threshold &&
                mouse_x < rect.roi_x + rect.roi_w + threshold &&
                mouse_y > rect.roi_y - threshold &&
                mouse_y < rect.roi_y + threshold){
                    console.log("tot");
                    return true;
                }
        
        else if (rect.roi_unlimited_left == true  &&
                mouse_y > rect.roi_y - threshold &&
                mouse_y < rect.roi_y + threshold && 
                mouse_x < rect.roi_x + rect.roi_w + threshold)
                {
                    console.log("tt");
                    return true;
                }
                
        else if (rect.roi_unlimited_right == true  &&
                mouse_y > rect.roi_y - threshold &&
                mouse_y < rect.roi_y + threshold && 
                mouse_x > rect.roi_x - threshold)
                {
                    console.log("tut");
                    return true;
                }

        else return false;
    }
    
    is_mouse_on_right_border_roi(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border_roi(rect);
    
        if (rect.x == 0 && rect.w == 0 && rect.y == 0 && rect.h == 0){
            return false;
        }
        
        if (rect.roi_unlimited_right == true ){
            return false;
        }
        else if (mouse_x > rect.roi_x + rect.roi_w - threshold &&
                mouse_x < rect.roi_x + rect.roi_w + threshold &&
                mouse_y > rect.roi_y - threshold &&
                mouse_y < rect.roi_h + rect.roi_y + threshold){
            return true;
        }

        else if (rect.roi_unlimited_up == true  &&
                mouse_x > rect.roi_x + rect.roi_w - threshold &&
                mouse_x < rect.roi_x + rect.roi_w + threshold &&
                
                mouse_y < rect.roi_y + rect.roi_h + threshold)
                {
                    console.log("tt");
                    return true;
                }
                
        else if (rect.roi_unlimited_down == true  &&
                mouse_x > rect.roi_x + rect.roi_w - threshold &&
                mouse_x < rect.roi_x + rect.roi_w + threshold &&
                
                mouse_y > rect.roi_y - threshold)
                {
                    console.log("tut");
                    return true;
                }
        else{
            return false;
        }
    }
    
    is_mouse_on_bottom_border_roi(e, rect)
    {
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        var threshold = this.calc_threshold_border_roi(rect);
    
        if (rect.x == 0 && rect.width == 0 && rect.y == 0 && rect.height == 0){
            return false;
        }
        
        
        if (rect.roi_unlimited_down == true ){
            return false;
        }
        else if (mouse_x > rect.roi_x - threshold &&
                mouse_x < rect.roi_x + rect.roi_w + threshold &&
                mouse_y > rect.roi_y + rect.roi_h - threshold &&
                mouse_y < rect.roi_y + rect.roi_h + threshold){
            return true;
        }
        else if (rect.roi_unlimited_left == true  &&
                mouse_y > rect.roi_y + rect.roi_h - threshold &&
                mouse_y < rect.roi_y + rect.roi_h + threshold && 
                mouse_x < rect.roi_x + rect.roi_w + threshold)
                {
                    console.log("tt");
                    return true;
                }
                
        else if (rect.roi_unlimited_right == true  &&
                mouse_y > rect.roi_y + rect.roi_h - threshold &&
                mouse_y < rect.roi_y + rect.roi_h + threshold && 
                mouse_x > rect.roi_x - threshold)
                {
                    console.log("tut");
                    return true;
                }
        else{
            return false;
        }
    }
    
    is_mouse_on_left_up_corner_roi(rect)
    {
    }
    
    is_mouse_on_right_up_corner_roi(rect)
    {
    }
    
    is_mouse_on_right_bottom_corner_roi(rect)
    {
    }
    
    is_mouse_on_left_bottom_corner_roi(rect)
    {
    }
    
    
    update_border(e){
    
        
        if(this.border_index == null) return;
        
        
        var rect = boxes[this.border_index];
            
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        
        if( this.mouse_is_on_left_up_corner_roi == true){
            
            //LEFT
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_width = rect.roi_w;
            var old_width = rect.w;
            
            rect.roi_x = mouse_x;
            rect.roi_w = (this.old_roi_x - mouse_x) + this.old_roi_w;

            
            
            if(rect.x < rect.roi_x){
                rect.x = rect.roi_x;
                rect.w = rect.w - (rect.x - old_x);
            }
                

            if(rect.w < 4){
                
                rect.x = this.old_x + this.old_w - 4;
                rect.w = 4;
                rect.roi_x = rect.x;
                rect.roi_w = this.old_roi_w - (rect.roi_x - this.old_roi_x);
            }
            
                        
            var x_offset =  old_x - rect.x;
                
            if (rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

            
            //TOP
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h;
            var old_height = rect.h;
            
            
            rect.roi_y = mouse_y;
            rect.roi_h = (this.old_roi_y - mouse_y) + (this.old_roi_h)

            
            
            if(rect.y < rect.roi_y){ 
                rect.y = rect.roi_y;
                rect.h = rect.h - (rect.y - old_y);
            }
                

            if(rect.h < 4){
                
                rect.y = this.old_y + this.old_h - 4;
                rect.h = 4;
                rect.roi_y = rect.y;
                rect.roi_h = this.old_roi_h - (rect.roi_y - this.old_roi_y);
            }
            
            var y_offset =  old_y - rect.y
                
            if (rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;


                
        }                  
        else if( this.mouse_is_on_right_up_corner_roi == true){

            //RIGHT
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_w = rect.roi_w;
            var old_width = rect.w;
            
            rect.roi_w = mouse_x - rect.roi_x;


            if(rect.x + rect.w > rect.roi_x + rect.roi_w){

                rect.w = rect.roi_x + rect.roi_w - rect.x;

            }
                
            if(rect.w < 4){

                rect.w = 4;

                rect.roi_w = (rect.x + rect.w) - rect.roi_x;
            }

        
            


            //TOP
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h; 
            var old_height = rect.h;
            
            
            rect.roi_y = mouse_y;
            rect.roi_h = (this.old_roi_y - mouse_y) + this.old_roi_h; //rect.roi_h + (rect.roi_y + self._main_text.y - mouse_y)

            
            
            if(rect.y < rect.roi_y){ //+ self._main_text.y){
                rect.y = rect.roi_y;
                rect.h = rect.h - (rect.y - old_y);
            }
                

            if(rect.h < 4){
                
                rect.y = this.old_y + this.old_h - 4;
                rect.h = 4;
                rect.roi_y = rect.y;
                rect.roi_h = this.old_roi_h - (rect.roi_y - this.old_roi_y);
            }
            
            var y_offset =  old_y - rect.y
                
            if (rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;

        }
      

                
        else if( this.mouse_is_on_right_bottom_corner_roi == true){

            //RIGHT
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_w = rect.roi_w;
            var old_width = rect.w;
            
            
            rect.roi_w = mouse_x - rect.roi_x;
          

            if(rect.x + rect.w > rect.roi_x + rect.roi_w) rect.w = rect.roi_x + rect.roi_w - rect.x;
                
            if(rect.w < 4){
                
                rect.w = 4;
                rect.roi_w = (rect.x + rect.w) - rect.roi_x;
            }

            //BOTTOM
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h;
            var old_height = rect.h;

            
            rect.roi_h = mouse_y - rect.roi_y;

            if(rect.y + rect.h > rect.roi_y + rect.roi_h) rect.h = rect.roi_y + rect.roi_h - rect.y;
                
            if(rect.h < 4){
                
                rect.h = 4;
                rect.roi_h = (rect.y + rect.h) - rect.roi_y;

            }
        }
                
        else if( this.mouse_is_on_left_bottom_corner_roi == true){


            //LEFT   
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_w = rect.roi_w; 
            var old_width = rect.w;
            
            
            rect.roi_x = mouse_x;
            rect.roi_w = (this.old_roi_x - mouse_x) + this.old_roi_w;

            
            
            if(rect.x < rect.roi_x){
                rect.x = rect.roi_x;
                rect.w = rect.w - (rect.x - old_x);
            }
                

            if(rect.w < 4){
                
                rect.x = this.old_x + this.old_w - 4;
                rect.w = 4;
                rect.roi_x = rect.x;
                rect.roi_w = this.old_roi_w - (rect.roi_x - this.old_roi_x);
            }
                
                            
            x_offset =  old_x - rect.x;
            
            if(rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

            
            //BOTTOM
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h;
            var old_height = rect.h;

            
            rect.roi_h = mouse_y - rect.roi_y


            if(rect.y + rect.h > rect.roi_y + rect.roi_h) rect.h = rect.roi_y + rect.roi_h - rect.y;

                
            if(rect.h < 4){
                rect.h = 4;
                rect.roi_h = (rect.y + rect.h) - rect.roi_y;
            }

        }

        
        else if(this.mouse_is_on_left_border_roi == true){
        
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_w = rect.roi_w; 
            var old_width = rect.w;
            
            
            rect.roi_x = mouse_x;
            rect.roi_w = (this.old_roi_x - mouse_x) + this.old_roi_w;

            
            
            if(rect.x < rect.roi_x){
                rect.x = rect.roi_x;
                rect.w = rect.w - (rect.x - old_x);
            }

            if(rect.w < 4){
                
                rect.x = this.old_x + this.old_w - 4;
                rect.w = 4;
                rect.roi_x = rect.x;
                rect.roi_w = this.old_roi_w - (rect.roi_x - this.old_roi_x);
            }
                            
            x_offset =  old_x - rect.x;
            
            if(rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

              
        }
        else if(this.mouse_is_on_top_border_roi == true){
        
                
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h; 
            var old_height = rect.h;
            
            
            rect.roi_y = mouse_y;
            rect.roi_h = (this.old_roi_y - mouse_y) + this.old_roi_h;

            
            
            if(rect.y < rect.roi_y){
                rect.y = rect.roi_y;
                rect.h = rect.h - (rect.y - old_y);
            }
                

            if(rect.h < 4){
                
                rect.y = this.old_y + this.old_h - 4;
                rect.h = 4;
                rect.roi_y = rect.y;
                rect.roi_h = this.old_roi_h - (rect.roi_y - this.old_roi_y);
            }
                
                            
            y_offset =  old_y - rect.y;
            
            if(rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;

        }
            
                
        else if(this.mouse_is_on_bottom_border_roi == true){

                
            var old_roi_y = rect.roi_y;
            var old_y = rect.y;
            var old_roi_height = rect.roi_h;
            var old_height = rect.h;

            
            rect.roi_h = mouse_y - rect.roi_y;

            if(rect.y + rect.h > rect.roi_y + rect.roi_h) rect.h = rect.roi_y + rect.roi_h - rect.y;
                
            if(rect.h < 4){

                rect.h = 4;
                rect.roi_h = (rect.y + rect.h) - rect.roi_y;
            }

        }
            
        else if(this.mouse_is_on_right_border_roi == true){
            
            var old_roi_x = rect.roi_x;
            var old_x = rect.x;
            var old_roi_w = rect.roi_w;
            var old_width = rect.w;
            
            rect.roi_w = mouse_x - rect.roi_x;


            if(rect.x + rect.w > rect.roi_x + rect.roi_w) rect.w = rect.roi_x + rect.roi_w - rect.x;
                
            if(rect.w < 4){

                rect.w = 4;
                rect.roi_w = (rect.x + rect.w) - rect.roi_x;
            }

        }
            
        else if( this.mouse_is_on_left_up_corner == true){

            //LEFT
            var old_x = rect.x;

            rect.x = mouse_x;
            rect.w = this.old_w + (this.old_x - mouse_x);
            
            
            if(rect.x < 1)rect.x = 1;
        
            if( mouse_x < rect.roi_x){
                rect.roi_w = rect.roi_w + (rect.roi_x - rect.x);
                rect.roi_x = rect.roi_x - (rect.roi_x - rect.x);
            }
                    
            
            if(rect.w < 4){
                rect.w = 4;
                rect.x = this.old_x + this.old_w - 4;
            }
                 
            x_offset =  old_x - rect.x;

                                    
            if(rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

   
            //TOP
            var old_y = rect.y;
            
        
            rect.y = mouse_y;
            rect.h = this.old_h + (this.old_y - mouse_y);
            
            
            if(rect.y < 1) rect.y = 1;
        
            if( mouse_y < rect.roi_y){

                rect.roi_h = rect.roi_h + (rect.roi_y - rect.y);
                rect.roi_y = rect.roi_y - (rect.roi_y - rect.y);
            }
            
            if(rect.h < 4){
                rect.h = 4;
                rect.y = this.old_y + this.old_h - 4;
            }
                 
            y_offset =  old_y - rect.y;

                                    
            if(rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;
            

        }
            
                
                
        else if( this.mouse_is_on_right_up_corner == true){


            //RIGHT
            old_width = rect.w;
            
            rect.w = mouse_x - rect.x;
            
            if(rect.x + rect.w > screen_w + 1) rect.w = screen_w - rect.x - 1;
            

            if( rect.x + rect.w > rect.roi_x + rect.roi_w) rect.roi_w = rect.roi_w + ((rect.x + rect.w) - (rect.roi_x + rect.roi_w));
            

            if(rect.w < 4) rect.w = 4;
            


            //TOP
            var old_y = rect.y;
            
        
            rect.y = mouse_y;
            rect.h = this.old_h + (this.old_y - mouse_y);
            
            
            if(rect.y < 1) rect.y = 1;
        
            if( mouse_y < rect.roi_y){

                rect.roi_h = rect.roi_h + (rect.roi_y - rect.y);
                rect.roi_y = rect.roi_y - (rect.roi_y - rect.y);
            }
            
            if(rect.h < 4){
                rect.h = 4;
                rect.y = this.old_y + this.old_h - 4;
            }
                 
            y_offset =  old_y - rect.y;

                                    
            if(rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;

        }
            
                
        else if( this.mouse_is_on_right_bottom_corner == true){
        
            //RIGHT
            old_width = rect.w;
            
            rect.w = mouse_x - rect.x;
            
            if(rect.x + rect.w > screen_w + 1) rect.w = screen_w - rect.x - 1;
            

            if( rect.x + rect.w > rect.roi_x + rect.roi_w) rect.roi_w = rect.roi_w + ((rect.x + rect.w) - (rect.roi_x + rect.roi_w));
            

            if(rect.w < 4) rect.w = 4;
            
            
            //BOTTOM
            var old_height = rect.h;
            
            rect.h = mouse_y - rect.y;
       
            if(rect.y + rect.h > screen_h + 1) rect.h = screen_h - rect.y - 1;
            
            

            if( rect.y + rect.h > rect.roi_y + rect.roi_h) rect.roi_h = rect.roi_h + ((rect.y + rect.h) - (rect.roi_y + rect.roi_h));
            

            
            if(rect.h < 4) rect.h = 4;
            
            
        }
                
        else if( this.mouse_is_on_left_bottom_corner == true){
            //LEFT
            var old_x = rect.x;

            rect.x = mouse_x;
            rect.w = this.old_w + (this.old_x - mouse_x);
            
            
            if(rect.x < 1)rect.x = 1;
        
            if( mouse_x < rect.roi_x){
                rect.roi_w = rect.roi_w + (rect.roi_x - rect.x);
                rect.roi_x = rect.roi_x - (rect.roi_x - rect.x);
            }
                    
            
            if(rect.w < 4){
                rect.w = 4;
                rect.x = this.old_x + this.old_w - 4;
            }
                 
            x_offset =  old_x - rect.x;

                                    
            if(rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

            
            //BOTTOM
            var old_height = rect.h;
            
            rect.h = mouse_y - rect.y;
       
            if(rect.y + rect.h > screen_h + 1) rect.h = screen_h - rect.y - 1;
            
            

            if( rect.y + rect.h > rect.roi_y + rect.roi_h) rect.roi_h = rect.roi_h + ((rect.y + rect.h) - (rect.roi_y + rect.roi_h));
            

            
            if(rect.h < 4) rect.h = 4;
        }
          
        else if(this.mouse_is_on_left_border == true){
            //LEFT
            var old_x = rect.x;

            rect.x = mouse_x;
            rect.w = this.old_w + (this.old_x - mouse_x);
            
            
            if(rect.x < 1)rect.x = 1;
        
            if( mouse_x < rect.roi_x){
                rect.roi_w = rect.roi_w + (rect.roi_x - rect.x);
                rect.roi_x = rect.roi_x - (rect.roi_x - rect.x);
            }
                    
            
            if(rect.w < 4){
                rect.w = 4;
                rect.x = this.old_x + this.old_w - 4;
            }
                 
            x_offset =  old_x - rect.x;

                                    
            if(rect.x_offset != null) rect.x_offset = rect.x_offset + x_offset;

          
        }
               
        else if(this.mouse_is_on_top_border == true){
            //TOP
            var old_y = rect.y;
            
        
            rect.y = mouse_y;
            rect.h = this.old_h + (this.old_y - mouse_y);
            
            
            if(rect.y < 1) rect.y = 1;
        
            if( mouse_y < rect.roi_y){

                rect.roi_h = rect.roi_h + (rect.roi_y - rect.y);
                rect.roi_y = rect.roi_y - (rect.roi_y - rect.y);
            }
            
            if(rect.h < 4){
                rect.h = 4;
                rect.y = this.old_y + this.old_h - 4;
            }
                 
            y_offset =  old_y - rect.y;

                                    
            if(rect.y_offset != null) rect.y_offset = rect.y_offset + y_offset;
        }       
        else if(this.mouse_is_on_bottom_border == true){
            //BOTTOM
            var old_height = rect.h;
            
            rect.h = mouse_y - rect.y;
       
            if(rect.y + rect.h > screen_h + 1) rect.h = screen_h - rect.y - 1;
            
            

            if( rect.y + rect.h > rect.roi_y + rect.roi_h) rect.roi_h = rect.roi_h + ((rect.y + rect.h) - (rect.roi_y + rect.roi_h));
            

            
            if(rect.h < 4) rect.h = 4;
        }
        else if(this.mouse_is_on_right_border == true){
                    
            //RIGHT
            old_width = rect.w;
            
            rect.w = mouse_x - rect.x;
            
            if(rect.x + rect.w > screen_w + 1) rect.w = screen_w - rect.x - 1;
            

            if( rect.x + rect.w > rect.roi_x + rect.roi_w) rect.roi_w = rect.roi_w + ((rect.x + rect.w) - (rect.roi_x + rect.roi_w));
            

            if(rect.w < 4) rect.w = 4;
        }
        
        
    }
    
    update_position(e){
    
        if (this.move_index == null) return;

        var rect = boxes[this.move_index];
        
        var old_x = rect.x;
        var old_width = rect.w;
        var old_y = rect.y;
        var old_height = rect.h;
        
            
        var mouse_x = parseInt(e.clientX);
        var mouse_y = parseInt(e.clientY);
        

        rect.x = mouse_x - this.position_offset_x;
        rect.y = mouse_y - this.position_offset_y;
        
        if  (rect.x + rect.w > screen_w) rect.x =  (screen_w-1) - rect.w;
            
        if (rect.x < 0) rect.x = 1;
 
        if  (rect.y + rect.h > screen_h) rect.y = (screen_h-1) - rect.h;
            
        if (rect.y < 0) rect.y = 1;
            

        if (rect.roi_x + rect.roi_w > screen_w) rect.roi_w = screen_w - rect.roi_x;
            
        if (rect.roi_y + rect.roi_h > screen_h) rect.roi_h = screen_h - rect.roi_y;
     
           
        if (rect.roi_x < 0)
        {
            var old_roi_x = rect.roi_x;
            rect.roi_x = 0;
                        
            var width_diff = rect.roi_x - old_roi_x;
            rect.roi_w = rect.roi_w - width_diff;
        }

            
        if (rect.roi_y < 0)
        {
            var old_roi_y = rect.roi_y;
            rect.roi_y = 0;
            
            var height_diff = rect.roi_y - old_roi_y;
            rect.roi_h = rect.roi_h - height_diff;
        }


        var x_offset =  old_x - rect.x;
        var y_offset =  old_y - rect.y;

        if (rect.x_offset != null && rect.y_offset != null)
        {
            rect.y_offset = rect.y_offset + y_offset;
            rect.x_offset = rect.x_offset + x_offset;
        }
            

        rect.roi_x = rect.roi_x - x_offset;
        rect.roi_y = rect.roi_y - y_offset;
    }
}



function set_rect_type(type, rect)  //default rect type
        {
            console.log("set rect type");
            var rect_features = rect.features["R"];
            
            var rect_half_w = Math.floor(rect.w/2);
            var rect_half_h = Math.floor(rect.h/2);
                
            if(type == "box")  //INPUT BOX
            {
                
                if (rect.is_main == true)
                {
                    rect_features["width"] = {"min":rect.w - rect_half_w, "max":screen_w};
                    rect_features["height"] = {"min":rect.h - 10, "max":rect.h + 10};  
                }
                else
                {
                    rect_features["width"] = {"min":rect.w - rect_half_w, "max":rect.roi_w};
                    rect_features["height"] = {"min":rect.h - 10, "max":rect.h + 10};  
                }
                
                rect.rect_type = "box";
            }
            else if (type == "window") //WINDOW
            {
                
                if (rect.is_main == true)
                {
                    rect_features["width"] = {"min":rect.w - rect_half_w, "max":screen_w};
                    rect_features["height"] = {"min":rect.h - rect_half_h, "max":screen_h}; 
                }
                else
                {
                    rect_features["width"] = {"min":rect.w - rect_half_w, "max":rect.roi_w};
                    rect_features["height"] = {"min":rect.h - rect_half_h, "max":rect.roi_h}; 
                }
                
                rect.rect_type = "window";
            }
            else //BUTTON
            {
                var min_w = rect.w - 9;
                var min_h = rect.h - 9;
                
                if (min_w < 4) min_w = 4;
                
                if (min_h < 4) min_h = 4;
                
                rect_features["width"] = {"min":min_w, "max": rect.w + 9};
                rect_features["height"] = {"min":min_h, "max":rect.h + 9};
                
                rect.rect_type = "button";
            
            }
            
            draw(rectManager.last_mouse_event);
        }
        
        function get_rect_type(rect)
        {     
            console.log("get rect type");
            var is_box = false;
            var is_window = false;
            var is_button = false;
            
            var rect_features = rect.features["R"];
            
            var rect_half_w = Math.floor(rect.w/2);
            var rect_half_h = Math.floor(rect.h/2);
            
            if (jQuery.isEmptyObject(rect_features))
            {
                if(rect.w >= rect.h * 8 && rect.h >= 15 && rect.h <= 50)  //INPUT BOX
                {
                    if (rect.is_main == true)
                    {
                        rect_features["width"] = {"min":rect.w - rect_half_w, "max":screen_w};
                    }
                    else
                    {
                        rect_features["width"] = {"min":rect.w - rect_half_w, "max":rect.roi_w};
 
                    }
                    
                    rect_features["height"] = {"min":rect.h - 10, "max":rect.h + 10}; 
                    
                    is_box = true;
                }
                else if (rect.w >= 120 && rect.h >= 120) //WINDOW
                {
                    if (rect.is_main == true)
                    {
                        rect_features["width"] = {"min":rect.w - rect_half_w, "max":screen_w};
                        rect_features["height"] = {"min":rect.h - rect_half_h, "max":screen_h}; 
                    }
                    else
                    {
                        rect_features["width"] = {"min":rect.w - rect_half_w, "max":rect.roi_w};
                        rect_features["height"] = {"min":rect.h - rect_half_h, "max":rect.roi_h}; 
                    }
                    
                    is_window = true;
                }
                else //BUTTON
                {
                    var min_w = rect.w - 9;
                    var min_h = rect.h - 9;
                    
                    if (min_w < 4) min_w = 4;
                    
                    if (min_h < 4) min_h = 4;
                    
                    rect_features["width"] = {"min":min_w, "max": rect.w + 9};
                    rect_features["height"] = {"min":min_h, "max":rect.h + 9};
                    
                    is_button = true;
                }
            }
            else
            {
                var min_w = rect_features["width"]["min"];
                var max_w = rect_features["width"]["max"];

                var min_h = rect_features["height"]["min"];
                var max_h = rect_features["height"]["max"]; 

                if (rect.is_main == true)
                {
                    if (min_w == rect.w - rect_half_w && max_w == screen_w && min_h == rect.h - 10, max_h == rect.h + 10)
                    {
                        is_box = true;
                    }
                    else if (min_w == rect.w - rect_half_w && max_w == screen_w && min_h == rect.h - rect_half_h && max_h == screen_h)
                    {  
                        is_window = true;
                    }
                    else
                    {
                        is_button = true;
                    }
                }
                else
                {
                    if (min_w == rect.w - rect_half_w && max_w == rect.roi_w && min_h == rect.h - 10, max_h == rect.h + 10)
                    {
                        is_box = true;
                    }
                    else if (min_w == rect.w - rect_half_w && max_w == rect.roi_w && min_h == rect.h - rect_half_h && max_h == rect.roi_h)
                    {  
                        is_window = true;
                    }
                    else
                    {
                        is_button = true;
                    }
                }
            }
            
            draw(rectManager.last_mouse_event);
            
            if (is_box)
            {
                rect.rect_type = "box";
                return "box";
            }
            
            if (is_window){
                rect.rect_type = "window";
                return "window";
            }
            
            if (is_button){
                rect.rect_type = "button";
                return "button";
            } 
            
                

        }
