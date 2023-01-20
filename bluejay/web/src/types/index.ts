interface Pickable {
  entry_conditions: {
    variable_name: string;
    verb: string;
    val: string;
  }[];
  available: boolean;
  chosen: boolean;
}

export interface Supernode extends Pickable {
  score: number;
}

export type Prompt = Pickable;

export type Subnode = Pickable;

export interface RGState {
  value: string;
  falsy: boolean;
}

export interface Message {
  text: string;
  source: string;
  error?: string;
  full_logs?: string[];
  supernodes?: Record<string, Supernode>;
  prompts?: Record<string, Prompt>;
  subnodes?: Record<string, Subnode>;
  rg_state?: Record<string, RGState>;
}
