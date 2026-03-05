/** Common API response types. */

export interface PaginatedResponse<T> {
    data: T[];
    meta: {
        page: number;
        page_size: number;
        total: number;
    };
}

export interface DataResponse<T> {
    data: T;
}

export interface ErrorResponse {
    detail: string;
    code: string;
}
