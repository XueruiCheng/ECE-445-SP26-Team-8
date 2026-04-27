export enum MirrorState {
  IDLE = 'idle',
  CAMERA = 'camera',
  INFERENCE = 'inference',
  OUTPUT = 'output'
}

export interface MatchResult {
  name: string;
  similarity: number;
  role: string;
  position: string;
  research_areas: string[];
  image_url: string;
  profile_url: string;
}
