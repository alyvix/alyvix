// Stores the currently-being-typechecked object for error messages.
let obj: any = null;
export class AxModelProxy {
  public readonly object_name: string;
  public readonly detection: DetectionProxy;
  public readonly box_list: BoxListEntityProxy[] | null;
  public readonly background: string;
  public static Parse(d: string): AxModelProxy {
    return AxModelProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): AxModelProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkString(d.object_name, false, field + ".object_name");
    d.detection = DetectionProxy.Create(d.detection, field + ".detection");
    checkArray(d.box_list, field + ".box_list");
    if (d.box_list) {
      for (let i = 0; i < d.box_list.length; i++) {
        d.box_list[i] = BoxListEntityProxy.Create(d.box_list[i], field + ".box_list" + "[" + i + "]");
      }
    }
    if (d.box_list === undefined) {
      d.box_list = null;
    }
    checkString(d.background, false, field + ".background");
    return new AxModelProxy(d);
  }
  private constructor(d: any) {
    this.object_name = d.object_name;
    this.detection = d.detection;
    this.box_list = d.box_list;
    this.background = d.background;
  }
}

export class DetectionProxy {
  public readonly type: string;
  public readonly timeout_s: number;
  public readonly break: boolean;
  public static Parse(d: string): DetectionProxy {
    return DetectionProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): DetectionProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkString(d.type, false, field + ".type");
    checkNumber(d.timeout_s, false, field + ".timeout_s");
    checkBoolean(d.break, false, field + ".break");
    return new DetectionProxy(d);
  }
  private constructor(d: any) {
    this.type = d.type;
    this.timeout_s = d.timeout_s;
    this.break = d.break;
  }
}

export class BoxListEntityProxy {
  public readonly x: number;
  public readonly y: number;
  public readonly w: number;
  public readonly h: number;
  public readonly roi_x: number;
  public readonly roi_y: number;
  public readonly roi_w: number;
  public readonly roi_h: number;
  public readonly roi_unlimited_left: boolean;
  public readonly roi_unlimited_up: boolean;
  public readonly roi_unlimited_right: boolean;
  public readonly roi_unlimited_down: boolean;
  public readonly group: number;
  public readonly is_main: boolean;
  public readonly thumbnail: ThumbnailProxy;
  public readonly type: string;
  public readonly features: FeaturesProxy;
  public readonly mouse: MouseProxy;
  public readonly keyboard: KeyboardProxy;
  public static Parse(d: string): BoxListEntityProxy {
    return BoxListEntityProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): BoxListEntityProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkNumber(d.x, false, field + ".x");
    checkNumber(d.y, false, field + ".y");
    checkNumber(d.w, false, field + ".w");
    checkNumber(d.h, false, field + ".h");
    checkNumber(d.roi_x, false, field + ".roi_x");
    checkNumber(d.roi_y, false, field + ".roi_y");
    checkNumber(d.roi_w, false, field + ".roi_w");
    checkNumber(d.roi_h, false, field + ".roi_h");
    checkBoolean(d.roi_unlimited_left, false, field + ".roi_unlimited_left");
    checkBoolean(d.roi_unlimited_up, false, field + ".roi_unlimited_up");
    checkBoolean(d.roi_unlimited_right, false, field + ".roi_unlimited_right");
    checkBoolean(d.roi_unlimited_down, false, field + ".roi_unlimited_down");
    checkNumber(d.group, false, field + ".group");
    checkBoolean(d.is_main, false, field + ".is_main");
    d.thumbnail = ThumbnailProxy.Create(d.thumbnail, field + ".thumbnail");
    checkString(d.type, false, field + ".type");
    d.features = FeaturesProxy.Create(d.features, field + ".features");
    d.mouse = MouseProxy.Create(d.mouse, field + ".mouse");
    d.keyboard = KeyboardProxy.Create(d.keyboard, field + ".keyboard");
    return new BoxListEntityProxy(d);
  }
  private constructor(d: any) {
    this.x = d.x;
    this.y = d.y;
    this.w = d.w;
    this.h = d.h;
    this.roi_x = d.roi_x;
    this.roi_y = d.roi_y;
    this.roi_w = d.roi_w;
    this.roi_h = d.roi_h;
    this.roi_unlimited_left = d.roi_unlimited_left;
    this.roi_unlimited_up = d.roi_unlimited_up;
    this.roi_unlimited_right = d.roi_unlimited_right;
    this.roi_unlimited_down = d.roi_unlimited_down;
    this.group = d.group;
    this.is_main = d.is_main;
    this.thumbnail = d.thumbnail;
    this.type = d.type;
    this.features = d.features;
    this.mouse = d.mouse;
    this.keyboard = d.keyboard;
  }
}

export class ThumbnailProxy {
  public readonly group: number;
  public readonly h: number;
  public readonly image: string;
  public readonly image_h: number;
  public readonly image_w: number;
  public readonly is_main: boolean;
  public readonly w: number;
  public readonly x: number;
  public readonly y: number;
  public static Parse(d: string): ThumbnailProxy {
    return ThumbnailProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): ThumbnailProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkNumber(d.group, false, field + ".group");
    checkNumber(d.h, false, field + ".h");
    checkString(d.image, false, field + ".image");
    checkNumber(d.image_h, false, field + ".image_h");
    checkNumber(d.image_w, false, field + ".image_w");
    checkBoolean(d.is_main, false, field + ".is_main");
    checkNumber(d.w, false, field + ".w");
    checkNumber(d.x, false, field + ".x");
    checkNumber(d.y, false, field + ".y");
    return new ThumbnailProxy(d);
  }
  private constructor(d: any) {
    this.group = d.group;
    this.h = d.h;
    this.image = d.image;
    this.image_h = d.image_h;
    this.image_w = d.image_w;
    this.is_main = d.is_main;
    this.w = d.w;
    this.x = d.x;
    this.y = d.y;
  }
}

export class FeaturesProxy {
  public readonly I: IProxy;
  public readonly R: RProxy;
  public readonly T: TProxy;
  public static Parse(d: string): FeaturesProxy {
    return FeaturesProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): FeaturesProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    d.I = IProxy.Create(d.I, field + ".I");
    d.R = RProxy.Create(d.R, field + ".R");
    d.T = TProxy.Create(d.T, field + ".T");
    return new FeaturesProxy(d);
  }
  private constructor(d: any) {
    this.I = d.I;
    this.R = d.R;
    this.T = d.T;
  }
}

export class IProxy {
  public readonly colors: boolean;
  public readonly likelihood: number;
  public static Parse(d: string): IProxy {
    return IProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): IProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkBoolean(d.colors, false, field + ".colors");
    checkNumber(d.likelihood, false, field + ".likelihood");
    return new IProxy(d);
  }
  private constructor(d: any) {
    this.colors = d.colors;
    this.likelihood = d.likelihood;
  }
}

export class RProxy {
  public readonly width: WidthOrHeightProxy | null;
  public readonly height: WidthOrHeight1Proxy | null;
  public static Parse(d: string): RProxy {
    return RProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): RProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    d.width = WidthOrHeightProxy.Create(d.width, field + ".width");
    if (d.width === undefined) {
      d.width = null;
    }
    d.height = WidthOrHeight1Proxy.Create(d.height, field + ".height");
    if (d.height === undefined) {
      d.height = null;
    }
    return new RProxy(d);
  }
  private constructor(d: any) {
    this.width = d.width;
    this.height = d.height;
  }
}

export class WidthOrHeightProxy {
  public readonly min: number;
  public readonly max: number;
  public static Parse(d: string): WidthOrHeightProxy | null {
    return WidthOrHeightProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): WidthOrHeightProxy | null {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      return null;
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, true);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, true);
    }
    checkNumber(d.min, false, field + ".min");
    checkNumber(d.max, false, field + ".max");
    return new WidthOrHeightProxy(d);
  }
  private constructor(d: any) {
    this.min = d.min;
    this.max = d.max;
  }
}

export class WidthOrHeight1Proxy {
  public readonly min: number;
  public readonly max: number;
  public static Parse(d: string): WidthOrHeight1Proxy | null {
    return WidthOrHeight1Proxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): WidthOrHeight1Proxy | null {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      return null;
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, true);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, true);
    }
    checkNumber(d.min, false, field + ".min");
    checkNumber(d.max, false, field + ".max");
    return new WidthOrHeight1Proxy(d);
  }
  private constructor(d: any) {
    this.min = d.min;
    this.max = d.max;
  }
}

export class TProxy {
  public readonly type: string | null;
  public static Parse(d: string): TProxy {
    return TProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): TProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkString(d.type, true, field + ".type");
    if (d.type === undefined) {
      d.type = null;
    }
    return new TProxy(d);
  }
  private constructor(d: any) {
    this.type = d.type;
  }
}

export class MouseProxy {
  public readonly features: Features1Proxy;
  public readonly type: string | null;
  public static Parse(d: string): MouseProxy {
    return MouseProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): MouseProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    d.features = Features1Proxy.Create(d.features, field + ".features");
    checkString(d.type, true, field + ".type");
    if (d.type === undefined) {
      d.type = null;
    }
    return new MouseProxy(d);
  }
  private constructor(d: any) {
    this.features = d.features;
    this.type = d.type;
  }
}

export class Features1Proxy {
  public readonly point: PointProxy;
  public readonly button: string;
  public readonly amount: number;
  public readonly delays_ms: number;
  public readonly pixels: number;
  public readonly direction: string | null;
  public static Parse(d: string): Features1Proxy {
    return Features1Proxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): Features1Proxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    d.point = PointProxy.Create(d.point, field + ".point");
    checkString(d.button, false, field + ".button");
    checkNumber(d.amount, false, field + ".amount");
    checkNumber(d.delays_ms, false, field + ".delays_ms");
    checkNumber(d.pixels, false, field + ".pixels");
    checkString(d.direction, true, field + ".direction");
    if (d.direction === undefined) {
      d.direction = null;
    }
    return new Features1Proxy(d);
  }
  private constructor(d: any) {
    this.point = d.point;
    this.button = d.button;
    this.amount = d.amount;
    this.delays_ms = d.delays_ms;
    this.pixels = d.pixels;
    this.direction = d.direction;
  }
}

export class PointProxy {
  public readonly dx: number;
  public readonly dy: number;
  public static Parse(d: string): PointProxy {
    return PointProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): PointProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkNumber(d.dx, false, field + ".dx");
    checkNumber(d.dy, false, field + ".dy");
    return new PointProxy(d);
  }
  private constructor(d: any) {
    this.dx = d.dx;
    this.dy = d.dy;
  }
}

export class KeyboardProxy {
  public readonly delays_ms: number;
  public readonly durations_ms: number;
  public readonly string: string;
  public static Parse(d: string): KeyboardProxy {
    return KeyboardProxy.Create(JSON.parse(d));
  }
  public static Create(d: any, field: string = 'root'): KeyboardProxy {
    if (!field) {
      obj = d;
      field = "root";
    }
    if (d === null || d === undefined) {
      throwNull2NonNull(field, d);
    } else if (typeof(d) !== 'object') {
      throwNotObject(field, d, false);
    } else if (Array.isArray(d)) {
      throwIsArray(field, d, false);
    }
    checkNumber(d.delays_ms, false, field + ".delays_ms");
    checkNumber(d.durations_ms, false, field + ".durations_ms");
    checkString(d.string, false, field + ".string");
    return new KeyboardProxy(d);
  }
  private constructor(d: any) {
    this.delays_ms = d.delays_ms;
    this.durations_ms = d.durations_ms;
    this.string = d.string;
  }
}

function throwNull2NonNull(field: string, d: any): never {
  return errorHelper(field, d, "non-nullable object", false);
}
function throwNotObject(field: string, d: any, nullable: boolean): never {
  return errorHelper(field, d, "object", nullable);
}
function throwIsArray(field: string, d: any, nullable: boolean): never {
  return errorHelper(field, d, "object", nullable);
}
function checkArray(d: any, field: string): void {
  if (!Array.isArray(d) && d !== null && d !== undefined) {
    errorHelper(field, d, "array", true);
  }
}
function checkNumber(d: any, nullable: boolean, field: string): void {
  if (typeof(d) !== 'number' && (!nullable || (nullable && d !== null && d !== undefined))) {
    errorHelper(field, d, "number", nullable);
  }
}
function checkBoolean(d: any, nullable: boolean, field: string): void {
  if (typeof(d) !== 'boolean' && (!nullable || (nullable && d !== null && d !== undefined))) {
    errorHelper(field, d, "boolean", nullable);
  }
}
function checkString(d: any, nullable: boolean, field: string): void {
  if (typeof(d) !== 'string' && (!nullable || (nullable && d !== null && d !== undefined))) {
    errorHelper(field, d, "string", nullable);
  }
}
function errorHelper(field: string, d: any, type: string, nullable: boolean): never {
  if (nullable) {
    type += ", null, or undefined";
  }
  throw new TypeError('Expected ' + type + " at " + field + " but found:\n" + JSON.stringify(d) + "\n\nFull object:\n" + JSON.stringify(obj));
}
