
import type { Shorts } from "@/redux/services/artistApislice";

export interface ReelsViewerProps {
  videos: Shorts[];
  startIndex: number;
  onClose: () => void;
}

export interface ReelComment {
  id?: number | string;

  username?: string;

  user?: {
    username?: string;
    avatar?: string;
  };

  text?: string;
  comment?: string;
  created_at?: string;

  likes_count?: number;
  is_liked?: boolean;
  replies_count?: number;
}

export interface ReelDetail {
  uuid?: string;
  caption?: string;

  user?: {
    username?: string;
    avatar?: string;
  };

  is_liked?: boolean;
  liked?: boolean;
  likes_count?: number;
  comments_count?: number;
}
export interface CommentItem {
    id?: number | string;
    username?: string;
  
    user?: {
      username?: string;
      avatar?: string;
    };
  
    text?: string;
    comment?: string;
    created_at?: string;
  
    likes_count?: number;
    is_liked?: boolean;
    replies_count?: number;
  }
  
  export interface ReelLikeState {
    [uuid: string]: boolean;
  }
  
  export interface ReelLikeCountState {
    [uuid: string]: number;
  }
  
  export interface ReelCommentCountState {
    [uuid: string]: number;
  }
  
  export interface CommentLikeState {
    [commentId: number]: boolean;
  }
  
  export interface CommentLikeCountState {
    [commentId: number]: number;
  }