class TableObject{
    
    constructor($table) {
        $table;
        
        $table.addClass("ta-table");
        
        this.$items = $table.find("div.ta");
		this.index = {};
		this.items = [];
        
        this.fill_items_list();
        
        this.position_items();
        
        this.draw_lines();
    }
    
    fill_items_list(){
    	// add items to index
        var _this = this;
		this.$items.each(function (i, el) {
			var $el = $(el);
			var id = $el.data('ta-id');
			var main_component = $el.data('ta-main');
			if(main_component === '') {
				main_component = undefined;
			}

			var item = {
				id: id,
				main_component: main_component,
				sub_components: [],
				el: $el,
				left: 0,
				width: $el.width() + 12
			};

			_this.index[id] = item;
			_this.items.push(item);
		});
        
        // make a graph from main_component relations
		this.items.forEach(function (item) {
			if (item.main_component !== undefined) {
				item.main_component = _this.index[item.main_component];
				item.main_component.sub_components.push(item);
			}
		});
    }
    
    position_items(){
    
        // pad items
		this.items.forEach(function (item) {

			item.left = 0;
			if (item.main_component !== undefined) {
				item.left = item.main_component.left + item.main_component.width;
			}
		});
        
        // position items
		this.items.forEach(function (item) {
			//console.log(el.left);
			item.el.css("left", item.left);
		});

		// wrap contents
		this.items.forEach(function (item) {
            //var a = item.el.children().find("div.content").length;
            if(item.el.find("div.content").length == 0)
            {
                item.el.html('<div class="content">' + item.el.html() + '</div>');
            }

		});

		// add main_component classes
		this.items.forEach(function (item) {
			if (item.sub_components.length > 0) {
				item.el.addClass("ta-main");
				item.shoSubs = true;
			}
		});
        
    }
    
    draw_lines()
    {
        //rimuovo le linee precedentemente disegnate
        this.items.forEach(function (item) {

            if (item.main_component === undefined) {
                return;
            }

            var $tails = $(".tail");
            
            $tails.remove();
            
            var b = 5;

            /*var $tail = $('<div class="tail"></div>').css({
                height: height,
                width: width,
                left: left
            });

            item.el.prepend($tail);*/
        });
        
        //return; 
        // draw lines
        this.items.forEach(function (item) {

            if (item.main_component === undefined) {
                return;
            }

            var childPos = item.el.position();
            var main_component = item.main_component;

            var main_componentPos = main_component.el.position();
            var height = childPos.top - main_componentPos.top;
            var width = item.left - main_component.left;
            var left = main_component.left - item.left + (main_component.width / 2);

            item.el.children('div.tail').first().remove();

            var $tail = $('<div class="tail"></div>').css({
                height: height,
                width: width,
                left: left
            });

            item.el.prepend($tail);
        });
    }
    
    
}