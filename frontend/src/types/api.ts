/** Common API response types. */

export interface DataResponse<T> {
    data: T;
}

export interface ErrorResponse {
    detail: string;
    code: string;
}
