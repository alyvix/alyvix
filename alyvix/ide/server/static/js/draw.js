var dpi = window.devicePixelRatio || 1;

function setRectangles(_boxes) {
    model.box_list = _boxes
    boxes = model.box_list;
    rectManager.set_rectangles(model.box_list);
    draw(rectManager.last_mouse_event);
}

function canvas_size(canvas) {
    if (ctx==null) return;
    //create a style object that returns width and height
      let style = {
        height() {
          return +getComputedStyle(canvas).getPropertyValue('height').slice(0,-2);
        },
        width() {
          return +getComputedStyle(canvas).getPropertyValue('width').slice(0,-2);
        }
      }
      
      return style
      

    }


function draw(e=null) {
    if (ctx==null) return; 

    
    //canvas = document.getElementById("myCanvas");
    //ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);


    //draw stuff!
    
    //ctx.strokeStyle = '#ff0000';
    //ctx.fillStyle = '#ff00ff';
    
    ctx.strokeStyle = '#0000ff';
    ctx.fillStyle = '#00aaff';
    
    if(rectManager.show_autocontoured_rects == true)
    {
        var rects = rectManager.get_rectangles();
        var autocontoured_rects = rectManager.get_autocontoured_rects();
    
        for(i=0; i<autocontoured_rects.length; i++)
        {
            var autocontoured_box = autocontoured_rects[i];
            
            /*if(rectManager.group == 0)
            {
                ctx.strokeStyle = '#ff0000';
                ctx.fillStyle = '#ff00ff'; 
            }
            else if (rectManager.group == 1)
            {
                ctx.strokeStyle = '#0000ff';
                ctx.fillStyle = '#0072ff';
            }
            else if (rectManager.group == 2)
            {
                ctx.strokeStyle = '#009500';
                ctx.fillStyle = '#00bc00';
            }
            */
           
            var match = false;

            for(j=0; j<rects.length; j++)
            {

                var box = rects[j];
                if(box.x == autocontoured_box.x && box.y == autocontoured_box.y &&
                    box.w == autocontoured_box.w && box.h == autocontoured_box.h)
                    {
                        if(box.group == 0)
                        {
                            ctx.strokeStyle = '#ff0000';
                            ctx.fillStyle = '#ff00ff'; 
                        } 
                        else if (box.group == 1)
                        {
                            ctx.strokeStyle = '#009500';
                            ctx.fillStyle = '#00bc00';
                        }
                        else if (box.group == 2)
                        {
                            ctx.strokeStyle = '#0000ff';
                            ctx.fillStyle = '#0072ff';
                        } 
                        
                        rectManager.draw_autocontoured_rect(ctx, box);
                        match = true; 
                    }
                
            }  
             
            if (match == false)
            {

                ctx.strokeStyle = '#656193';
                ctx.globalAlpha=0.3;
                ctx.fillStyle="#515285"; 
                ctx.fillRect(autocontoured_box.x, autocontoured_box.y,
                            autocontoured_box.w, autocontoured_box.h);
                            
                ctx.globalAlpha=1;
                            
                ctx.strokeRect(autocontoured_box.x, autocontoured_box.y,
                              autocontoured_box.w, autocontoured_box.h);
                                    
            }

            
            ctx.fillStyle = '#AC60F6';
        }
    }
    else
    {
                
        var rectangles = rectManager.get_rectangles();
    
        for(i=0; i<rectangles.length; i++)  
        {
            var box = rectangles[i];
            
            if(box.group == 0)
            {
                ctx.strokeStyle = '#ff0000';
                
                if (box.is_main) ctx.fillStyle = '#ff00ff';
                else ctx.fillStyle = '#ff00ff'; //'#AC60F6';
            }
            else if (box.group == 1)
            {
                ctx.strokeStyle = '#009500';
                if (box.is_main) ctx.fillStyle = '#00bc00';
                else ctx.fillStyle = '#00bc00'; //'#4ca737';
            }
            else if (box.group == 2)
            {

                ctx.strokeStyle = '#0000ff';
                if (box.is_main) ctx.fillStyle = '#0072ff';
                else ctx.fillStyle = '#0072ff'; //'#50a5d6';
            }
            
            rectManager.draw_rect(ctx, box, i);
            
            
            ctx.fillStyle = '#AC60F6';
        }
        
        if(e != null && rectManager.capturing_rect == true)
        {
            if ((rectManager.group == 0 && rectManager.g0_elements_cnt < 5) || (rectManager.group == 1 && rectManager.g1_elements_cnt < 5) || 
                (rectManager.group == 2 && rectManager.g2_elements_cnt < 5))
            {
                var mouseX=parseInt(e.clientX);
                var mouseY=parseInt(e.clientY);
                
                //ctx.strokeStyle = '#00ff00';
                

                                
                ctx.globalAlpha=0.3;
                //ctx.fillStyle="#20b2aa"; 
                
                
                if(rectManager.group == 0)
                {
                    ctx.strokeStyle = '#ff0000';
                    ctx.fillStyle = '#ff00ff';
                }
                else if (rectManager.group == 1)
                {
                    ctx.strokeStyle = '#009500';
                    ctx.fillStyle = '#00bc00';
                }
                else if (rectManager.group == 2)
                {

                    ctx.strokeStyle = '#0000ff';
                    ctx.fillStyle = '#0072ff';
                }
                
                
                
                ctx.fillRect(rectManager.click_position_x, rectManager.click_position_y,
                                mouseX - rectManager.click_position_x, mouseY - rectManager.click_position_y);
                                
                ctx.globalAlpha=1;
                                
                ctx.strokeRect(rectManager.click_position_x, rectManager.click_position_y,
                                mouseX - rectManager.click_position_x, mouseY - rectManager.click_position_y);
            }                    
            
        }
            
        
        if(e != null && rectManager.border_index == null && rectManager.move_index == null &&
            rectManager.mouse_is_on_border == null && rectManager.mouse_is_inside_rectangle == null && ttWIndow_isOpen == false)
        {
        
            if ((rectManager.group == 0 && rectManager.g0_elements_cnt < 5) || (rectManager.group == 1 && rectManager.g1_elements_cnt < 5) || 
                (rectManager.group == 2 && rectManager.g2_elements_cnt < 5))
            {
                mouseX=parseInt(e.clientX);
                mouseY=parseInt(e.clientY);
                
                //ctx.fillStyle = '#AC60F6';
                
                if (rectManager.group == 0)
                {
                    ctx.strokeStyle = '#ff00ff';
                    ctx.globalAlpha=0.7;
                }
                
                if (rectManager.group == 1)
                {
                    ctx.strokeStyle = '#00bc00';
                    ctx.globalAlpha=0.7;
                }
                
                if (rectManager.group == 2)
                {

                    ctx.strokeStyle = '#0072ff';
                    ctx.globalAlpha=0.7;
                }
                

                

                //draw line
                ctx.beginPath();
                    //ctx.lineWidth = 0.5;
                    //vertical top
                    //ctx.lineDashOffset = 2;
                    
                                        
                    //ctx.moveTo(0, mouseY -5);
                    //ctx.lineTo(+getComputedStyle(canvas).getPropertyValue('width').slice(0,-2) - 900, mouseY -5);
                    //ctx.stroke();
                    
                    //ctx.setLineDash([0.5,1.5]); //larghezza dot, larghezza spazio
                    
                    ctx.moveTo(mouseX, 0);
                    ctx.lineTo(mouseX, +getComputedStyle(canvas).getPropertyValue('height').slice(0,-2));

                    ctx.moveTo(0, mouseY);
                    ctx.lineTo(+getComputedStyle(canvas).getPropertyValue('width').slice(0,-2), mouseY);



                    //ctx.strokeStyle = '#000000';
                    ctx.stroke();
                
                ctx.closePath();
                //ctx.translate(-0.5, -0.5);
            }
            
            
        }
    }
    
}