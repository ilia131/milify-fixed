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