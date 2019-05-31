export interface AxModel {
    object_name: string;
    detection: Detection;
    box_list?: (BoxListEntity)[] | null;
    background: string;
  }
  export interface Detection {
    type: string;
    timeout_s: number;
    break: boolean;
  }
  export interface BoxListEntity {
    x: number;
    y: number;
    w: number;
    h: number;
    roi_x: number;
    roi_y: number;
    roi_w: number;
    roi_h: number;
    roi_unlimited_left: boolean;
    roi_unlimited_up: boolean;
    roi_unlimited_right: boolean;
    roi_unlimited_down: boolean;
    group: number;
    is_main: boolean;
    thumbnail: Thumbnail;
    type: string;
    features?: Features;
    mouse?: Mouse;
    keyboard?: Keyboard;
  }
  export interface Thumbnail {
    group: number;
    h: number;
    image: string;
    image_h: number;
    image_w: number;
    is_main: boolean;
    w: number;
    x: number;
    y: number;
  }
  export interface Features {
    I: I;
    R: R;
    T: T;
  }
  export interface I {
    colors: boolean;
    likelihood: number;
  }
  export interface R {
    width?: WidthOrHeight | null;
    height?: WidthOrHeight | null;
  }
  export interface WidthOrHeight {
    min: number;
    max: number;
  }

  export interface T {
    type?: string | null;
  }
  export interface Mouse {
    features: Features1;
    type?: string | null;
  }
  export interface Features1 {
    point: Point;
    button?: string;
    amount?: number;
    delays_ms?: number;
    pixels?: number;
    direction?: string | null;
  }
  export interface Point {
    dx: number;
    dy: number;
  }
  export interface Keyboard {
    delays_ms: number;
    durations_ms: number;
    string: string;
  }
  