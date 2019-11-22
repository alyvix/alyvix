import { BehaviorSubject, Observable } from "rxjs";
import { Injectable, Inject } from "@angular/core";
import { BoxListEntity, AxModel } from "../ax-model/model";
import { DesignerGlobal, GroupsFlag } from "./ax-global";

import { moveItemInArray } from '@angular/cdk/drag-drop';


import * as _ from 'lodash';
import * as fastDeepEqual from 'fast-deep-equal';
import { HotkeysService, Hotkey } from "angular2-hotkeys";
import { AlyvixApiService } from "../alyvix-api.service";



export interface TreeNode {
  children?: TreeNode[],
  box?: BoxListEntity,
  image?: string
  last: boolean
}

@Injectable({
  providedIn: 'root'
})
export class AxDesignerService {


  constructor(
    @Inject('GlobalRefDesigner') private global: DesignerGlobal,
    @Inject("subSystem") private subSystem:string,
    private api: AlyvixApiService
  ) {
    this.global.axModel().subscribe(axModel => {
      if(axModel) {
        console.log("AAAA")
        console.log(axModel);
        this.axModel = axModel;
        console.log(axModel)
        if (axModel.box_list) {
          axModel.box_list.forEach(box => {
            if (!box.features.I.likelihood) {
              box.features.I = { 'colors': true, 'likelihood': 0.9 }
            }
          })
        }

        this.flags = this.global.getGroupsFlag();

        var iSelectedNode = this.global.getSelectedNode() //needs to be done before loadNodes because loadNodes call setSelectedNode

        var lastElement = this.global.lastElement()


        this._loadNodes(true);

        var selectedNode: TreeNode = null;
        if (lastElement) {

          selectedNode = this.findNode(lastElement)
          this.global.setSelectedNode(this.indexOfBox(lastElement))

        } else if (iSelectedNode >= 0) {
          this.global.setSelectedNode(iSelectedNode);
          var node = axModel.box_list[iSelectedNode];
          selectedNode = this.findNode(node)

        }
        if (selectedNode)
          this._selectedNode.next(selectedNode)
      }
    });






  }

  private _selectedNode: BehaviorSubject<TreeNode> = new BehaviorSubject<TreeNode>(null);
  private _root: BehaviorSubject<TreeNode> = new BehaviorSubject<TreeNode>(null);

  private _dragging: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  private flatBoxes(): TreeNode[] {
    var nodes: TreeNode[] = [];
    nodes.push(this._root.value);
    if (this._root.value.children) {
      this._root.value.children.forEach(n => {
        nodes.push(n);
        if (n.children) {
          n.children.forEach(sb => nodes.push(sb));
        }
      })
    }
    return nodes;
  }

  private flatBoxList(): BoxListEntity[] {
    return this.flatBoxes().filter(x => x.box).map(x => x.box)
  }

  private findNode(box: BoxListEntity): TreeNode {
    var selectedNode: TreeNode
    if (box && box.is_main) {
      selectedNode = this._root.value.children.find(x => fastDeepEqual(x.box, box))
    } else {
      var zero: TreeNode[] = []
      selectedNode = this._root.value.children.reduce((a, b) => a.concat(b.children), zero).find(x => fastDeepEqual(x.box, box))
    }
    return selectedNode
  }



  public setSelectedNode(box: TreeNode) {
    var selectedNode = this.indexOfBox(box.box)
    this._selectedNode.next(box);
    this.global.setSelectedNode(selectedNode);
  }

  public getSelectedNode(): Observable<TreeNode> {
    return this._selectedNode;
  }

  public setDragging(drag: boolean) {
    this._dragging.next(drag);
  }

  public getDragging(): Observable<boolean> {
    return this._dragging;
  }




  axModel:AxModel;
  flags: GroupsFlag

  private indexOfBox(box: BoxListEntity): number {
    var index = 0;
    if (box) {
      index = this.axModel.box_list.findIndex(b => fastDeepEqual(b, box));
    }
    return index;
  }

  public indexSelectedNode(node: TreeNode): number {
    if (node && node.box) {
      var result = 0;
      this.flatBoxes().forEach((n, i) => {
        if (n.box && fastDeepEqual(n.box, node.box)) {
          result = i
        }
      });
      return result;
    } else return 0
  }



  private static boxListEntityToNode(box: BoxListEntity): TreeNode {
    var result: TreeNode = {
      box: box,
      last: false
    }

    if (box.thumbnail) {
      result.image = 'data:image/jpg;base64,' + box.thumbnail.image;
    }

    return result;
  }

  getRoot(): Observable<TreeNode> {
    return this._root;
  }

  getModel(): AxModel {
    return this.axModel;
  }

  private _loadNodes(selectRoot: boolean) {

    var box_list = [];
    if (this.axModel.box_list) {
      box_list = this.axModel.box_list;
    }

    var boxByGroups = _.groupBy(box_list, function (box: BoxListEntity) { return box.group })


    var groups: TreeNode[] = _.map(boxByGroups, function (elements: BoxListEntity[], group: number) {
      var mainNode = AxDesignerService.boxListEntityToNode(elements.find(x => x.is_main));
      var children: TreeNode[] = elements.filter(x => !x.is_main).map(box => AxDesignerService.boxListEntityToNode(box))

      if (children.length > 0) {
        children[children.length - 1].last = true;
      }

      mainNode.children = children;
      return mainNode;
    });

    if (groups.length > 0) {
      groups[groups.length - 1].last = true;
    }

    var root = { children: groups, image: this.axModel.background, last: true }
    console.log(root);
    this._root.next(root);

    if (selectRoot) {
      this.setSelectedNode(root);
    }
    this.updateFlags()

    this.updateAx();


  }

  updateFlags() {
    [0, 1, 2].forEach(i => {
      this.flags.count[i] = this.groupCount(i)
      this.flags.created[i] = this.flags.count[i] > 0
      this.flags.main[i] = this.axModel.box_list.filter(x => x.group == i && x.is_main).length > 0;
    });
    this.global.setGroupFlags(this.flags);
  }

  groupCount(group: number): number {
    if (this.axModel.box_list) {
      return this.axModel.box_list.filter(x => x.group == group).length
    }
    return 0;
  }

  isGroupFull(group: number): boolean {
    return this.groupCount(group) > 4;
  }

  availableGroups(): boolean {
    return this.groupCount(2) == 0
  }

  full(): boolean {
    return [0, 1, 2].every(x => this.isGroupFull(x))
  }


  removeAll() {
    this.axModel.box_list.length = 0;
    this._loadNodes(true);
  }
  newComponent(node: TreeNode) {

    if (node.box && !this.isGroupFull(node.box.group)) {
      this.global.newComponent(node.box.group)
    } else {
      var availableGroup = [0, 1, 2].find(i => !this.isGroupFull(i));
      if (availableGroup >= 0) {
        this.global.newComponent(availableGroup);
      }
    }
  }
  removeGroup(node: TreeNode) {
    this.axModel.box_list = this.axModel.box_list.filter(n => n.group != node.box.group)
    for (var i = node.box.group; i < 3; i++) {
      this.axModel.box_list.filter(x => x.group - 1 == i).forEach(n => n.group = i);
    }
    this._loadNodes(false);
  }
  duplicateGroup(node: TreeNode) {
    var group = node.box.group;
    var nextGroup = _.maxBy(this.axModel.box_list, function (x: BoxListEntity) { return x.group }).group + 1;
    if (nextGroup < 3) {
      var groupToClone = this.axModel.box_list.filter(x => x.group == group);
      var newGroup = _.cloneDeep(groupToClone).map(x => {
        x.id = this.global.uuidv4();
        x.group = nextGroup
        return x;
      })
      this.axModel.box_list = this.axModel.box_list.concat(newGroup);
      this._loadNodes(false);
      var toSelect = this._root.value.children[nextGroup];
      if (toSelect) {
        this.setSelectedNode(toSelect)
      }
    }
  }
  detectAs(type: string, node: TreeNode) {
    node.box.type = type;
  }
  removeComponent(node: TreeNode) {
    this.axModel.box_list = this.axModel.box_list.filter(x => !fastDeepEqual(x, node.box));
    this._loadNodes(false);
  }
  duplicateComponent(node: TreeNode) {
    if (!this.isGroupFull(node.box.group)) {
      var i = this.indexOfBox(node.box);
      var component = _.cloneDeep(node.box);
      component.id = this.global.uuidv4();
      this.axModel.box_list.splice(i + 1, 0, component);
      this._loadNodes(false);
      var toSelect = this._root.value.children[node.box.group].children.find(x => x.box.id == component.id)
      if (toSelect) {
        this.setSelectedNode(toSelect);
      }
    }
  }
  setAsMain(node: TreeNode) {
    var oldmain = this.axModel.box_list.findIndex(x => x.group == node.box.group && x.is_main);
    var newmain = this.indexOfBox(node.box);
    var temp = this.axModel.box_list[oldmain];
    this.axModel.box_list[oldmain] = this.axModel.box_list[newmain];
    this.axModel.box_list[newmain] = temp;
    this.axModel.box_list[oldmain].is_main = true;
    this.axModel.box_list[newmain].is_main = false;
    this._loadNodes(false);
  }

  setPoint(node: TreeNode) {
    if (node.box) {
      var i = this.indexOfBox(node.box)
      this.global.setPoint(i)
    }
  }

  public updateAx() {
    this.axModel.box_list = this.flatBoxList();
    this.global.setRectangles();
  }


  save() {
    this.updateAx();
    this.api.saveObject(this.axModel).subscribe(x => {
      if (this.subSystem === 'designer') {
        this.api.closeDesiger();
      }
    });
  }

  cancel() {
    this.api.closeDesiger();
  }


}
