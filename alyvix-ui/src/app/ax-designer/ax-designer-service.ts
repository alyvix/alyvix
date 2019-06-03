import { BehaviorSubject, Observable } from "rxjs";
import { Injectable, Inject } from "@angular/core";
import { BoxListEntity, AxModel } from "../ax-model/model";
import { GlobalRef, GroupsFlag } from "../ax-model/ax-global";

import {  moveItemInArray } from '@angular/cdk/drag-drop';


import * as _ from 'lodash';
import { HotkeysService, Hotkey } from "angular2-hotkeys";



export interface TreeNode{
    children?: TreeNode[],
    box?:BoxListEntity,
    image?:string
    last:boolean
  }

@Injectable({
    providedIn: 'root'
  })
export class AxDesignerService {


    constructor( @Inject('GlobalRef') private global: GlobalRef, private _hotkeysService: HotkeysService) {
        this.axModel = this.global.nativeGlobal().axModel();
        if(this.axModel.box_list) {
            this.axModel.box_list.forEach(box => {
                if(!box.features.I.likelihood) {
                    box.features.I = {'colors': true, 'likelihood': 0.9}
                }
            })
        }

        this.flags = this.global.nativeGlobal().getGroupsFlag();

        var iSelectedNode = this.global.nativeGlobal().getSelectedNode() //needs to be done before loadNodes because loadNodes call setSelectedNode

        this._loadNodes();

        var selectedNode:TreeNode = null;
        
        if(iSelectedNode >= 0) {
            var node = this.axModel.box_list[iSelectedNode];
            if(node && node.is_main) {
                selectedNode = this._root.value.children.find(x => x.box == node)
            } else {
                var zero:TreeNode[] = []
                selectedNode = this._root.value.children.reduce( (a,b) => a.concat(b.children), zero).find(x => x.box == node)
            }
               
        }
        if(selectedNode)    
            this._selectedNode.next(selectedNode)
        


        this._hotkeysService.add(new Hotkey('ctrl+x', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(!node) return false;
            if(!node.box) {
                this.removeAll()
            } else if(node.box.is_main) {
                this.removeGroup(node)
            } else {
                this.removeComponent(node)
            }
            return false; // Prevent bubbling
        },undefined,'Remove elements/group/component'));

        this._hotkeysService.add(new Hotkey('ctrl+d', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node && node.box) {
                if(node.box.is_main) {
                    this.duplicateGroup(node)
                } else {
                    this.duplicateComponent(node)
                }
            }
            return false; // Prevent bubbling
        },undefined,'Duplicate selected group/component'));

        this._hotkeysService.add(new Hotkey('ctrl+i', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node && node.box) {
                this.detectAs('I',node)
            }
            return false; // Prevent bubbling
        },undefined,'Detect as Image'));

        this._hotkeysService.add(new Hotkey('ctrl+r', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node && node.box) {
                this.detectAs('R',node)
            }
            return false; // Prevent bubbling
        },undefined,'Detect as Rectangle'));

        this._hotkeysService.add(new Hotkey('ctrl+t', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node && node.box && !node.box.is_main) {
                this.detectAs('T',node)
            }
            return false; // Prevent bubbling
        },undefined,'Detect as Text'));

        this._hotkeysService.add(new Hotkey('ctrl+m', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node && node.box && !node.box.is_main) {
                this.setAsMain(node)
            }
            return false; // Prevent bubbling
        },undefined,'Set as main'));

        this._hotkeysService.add(new Hotkey('ctrl+n', (event: KeyboardEvent): boolean => {
            var node = this._selectedNode.getValue()
            if(node) 
                this.newComponent(node)
            return false; // Prevent bubbling
        },undefined,'New component'));

    }

    private _selectedNode:BehaviorSubject<TreeNode> = new BehaviorSubject<TreeNode>(null);
    private _root:BehaviorSubject<TreeNode> = new BehaviorSubject<TreeNode>(null);

    private _dragging:BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

    private flatBoxes():TreeNode[] {
        var nodes:TreeNode[] = [];
        nodes.push(this._root.value);
        if(this._root.value.children) {
            this._root.value.children.forEach(n => {
                nodes.push(n);
                if(n.children) {
                    n.children.forEach(sb => nodes.push(sb));
                }
            })
        }
        return nodes;
    }

    private flatBoxList():BoxListEntity[] {
        return this.flatBoxes().filter(x => x.box).map(x => x.box)
    }
 
    public indexSelectedNode(node:TreeNode):number {
        if(node.box) {
            this.flatBoxes().indexOf(node);
        } else return 0
    }

    public setSelectedNode(box:TreeNode) {
        var selectedNode = null;
        if(box.box) {
            selectedNode = this.axModel.box_list.indexOf(box.box)
        }
        this._selectedNode.next(box);
        this.global.nativeGlobal().setSelectedNode(selectedNode);
    }

    public getSelectedNode():Observable<TreeNode> {
        return this._selectedNode;
    }

    public setDragging(drag: boolean) {
        this._dragging.next(drag);
    }

    public getDragging():Observable<boolean> {
        return this._dragging;
    }




    axModel:AxModel
    flags:GroupsFlag
  
    private static boxListEntityToNode(box:BoxListEntity):TreeNode {
      var result:TreeNode =  {
        box: box,
        last: false
      }
  
      if(box.thumbnail) {
        result.image = 'data:image/jpg;base64,' + box.thumbnail.image;
      }
  
      return result;
    }
  
    getRoot():Observable<TreeNode> {
        return this._root;
    }

    getModel():AxModel {
        return this.axModel;
    }
  
    private _loadNodes() {
  
      var box_list = [];
      if(this.axModel.box_list) {
          box_list = this.axModel.box_list;
      }
  
      var boxByGroups = _.groupBy(box_list, function(box:BoxListEntity) { return box.group})
  
  
      var groups:TreeNode[] = _.map(boxByGroups, function(elements:BoxListEntity[],group:number) {
        var mainNode = AxDesignerService.boxListEntityToNode(elements.find(x => x.is_main));
        var children:TreeNode[] = elements.filter(x => !x.is_main).map(box => AxDesignerService.boxListEntityToNode(box))
  
        if(children.length > 0) {
          children[children.length - 1].last = true;
        }
        
        mainNode.children = children;
        return mainNode;
      });
  
      if(groups.length > 0) {
        groups[groups.length - 1].last = true;
      }
  
      var root = { children: groups, image: this.axModel.background, last: true}
  
      this._root.next(root);
  
      this.setSelectedNode(root);
      this.updateFlags()

      this.updateAx();

      console.log("reloaded boxes")

    }

    updateFlags() {
        [0,1,2].forEach(i => {
            this.flags.count[i] = this.groupCount(i)
            this.flags.created[i] = this.flags.count[i] > 0
            this.flags.main[i] = this.axModel.box_list.filter(x => x.group == i && x.is_main).length > 0;
        });
        this.global.nativeGlobal().setGroupFlags(this.flags);
    }

    groupCount(group:number):number {
        if(this.axModel.box_list) {
            return this.axModel.box_list.filter(x => x.group == group).length
        }
        return 0;
    }

    isGroupFull(group:number):boolean {
        return this.groupCount(group) > 4;
    }

    availableGroups():boolean {
        return this.groupCount(2) == 0
    }

    full():boolean {
        return [0,1,2].every(x => this.isGroupFull(x))
    }
  
  
    removeAll() {
        this.axModel.box_list.length = 0;
        this._loadNodes();
    }
    newComponent(node:TreeNode) {
        
        if(node.box && !this.isGroupFull(node.box.group)) {
            console.log("create new component")
            this.global.nativeGlobal().newComponent(node.box.group)
        }
        var availableGroup = [0,1,2].find(i => !this.isGroupFull(i));
        console.log(availableGroup);
        if(availableGroup >= 0) {
            console.log("create new component")
            this.global.nativeGlobal().newComponent(availableGroup);
        }
    }
    removeGroup(node:TreeNode) {
        console.log("remove Group")
        this.axModel.box_list = this.axModel.box_list.filter(n => n.group != node.box.group)
        for(var i = node.box.group; i < 3; i++) {
            this.axModel.box_list.filter(x => x.group - 1 == i).forEach(n => n.group = i);
        }
        this._loadNodes();
    }
    duplicateGroup(node:TreeNode) {
        console.log("Douplicate group");
        var group = node.box.group;
        var nextGroup = _.maxBy(this.axModel.box_list,function(x:BoxListEntity) {return x.group}).group + 1;
        console.log(nextGroup)
        if(nextGroup < 3) {
            var groupToClone = this.axModel.box_list.filter(x => x.group == group);
            console.log(groupToClone)
            var newGroup = _.cloneDeep(groupToClone).map(x => {
                x.group = nextGroup
                return x;
            })
            console.log(newGroup)
            this.axModel.box_list = this.axModel.box_list.concat(newGroup);
            this._loadNodes();
            var toSelect = this._root.value.children[nextGroup];
            console.log(toSelect)
            if(toSelect) {
                this.setSelectedNode(toSelect)
            }
        }
    }
    detectAs(type:string,node:TreeNode) {
        node.box.type = type;
    }
    removeComponent(node:TreeNode) {
        this.axModel.box_list = this.axModel.box_list.filter(x => x != node.box);
        this._loadNodes();
    }
    duplicateComponent(node:TreeNode) {
        if(!this.isGroupFull(node.box.group)) {
            var i = this.axModel.box_list.indexOf(node.box);
            var component = _.cloneDeep(node.box);
            this.axModel.box_list.splice(i+1,0,component);
            this._loadNodes();
            var toSelect = this._root.value.children[node.box.group].children.find(x => x.box == component)
            if(toSelect) {
                this.setSelectedNode(toSelect);
            }
        }
    }
    setAsMain(node:TreeNode) {
        var oldmain = this.axModel.box_list.findIndex(x => x.group == node.box.group && x.is_main);
        var newmain = this.axModel.box_list.indexOf(node.box);
        var temp = this.axModel.box_list[oldmain];
        this.axModel.box_list[oldmain] = this.axModel.box_list[newmain];
        this.axModel.box_list[newmain] = temp;
        this.axModel.box_list[oldmain].is_main = true;
        this.axModel.box_list[newmain].is_main = false;
        this._loadNodes();
    }

    setPoint(node:TreeNode) {
        if(node.box) {
            var i = this.axModel.box_list.indexOf(node.box)
            this.global.nativeGlobal().setPoint(i)
        }
    }

    updateAx() {
        this.axModel.box_list = this.flatBoxList();
        this.global.nativeGlobal().setRectangles();
    }


    save() {
        this.updateAx();
        this.global.nativeGlobal().save();
    }

    cancel() {
        this.global.nativeGlobal().cancel();
    }


}