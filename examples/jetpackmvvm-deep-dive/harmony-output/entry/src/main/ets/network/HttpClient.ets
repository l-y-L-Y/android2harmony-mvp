import { http } from '@kit.NetworkKit';
import { MockServer } from '../common/MockServer';

export class NetworkConfig {
  static useMock: boolean = true;
}

export class HttpParams {
  items: HttpParam[] = [];

  set(key: string, value: string | number): void {
    this.items.push(new HttpParam(key, value));
  }
}

export class HttpParam {
  key: string;
  value: string | number;

  constructor(key: string, value: string | number) {
    this.key = key;
    this.value = value;
  }
}

export class NetworkError extends Error {
  url: string;
  statusCode: number;

  constructor(url: string, message: string, statusCode: number = 0) {
    super(message);
    this.url = url;
    this.statusCode = statusCode;
  }
}

export class MigratedHttpClient {
  private readonly baseUrl: string = 'https://example.com/';

  async get(path: string, params: HttpParams = new HttpParams()): Promise<Object> {
    const url = this.buildUrl(path, params);
    return this.requestJson(url, http.RequestMethod.GET);
  }

  private buildUrl(path: string, params: HttpParams): string {
    let resolved = path;
    params.items.forEach((item: HttpParam) => {
      resolved = resolved.replace(`{${item.key}}`, String(item.value));
    });
    const query = params.items
      .filter((item: HttpParam) => !path.includes(`{${item.key}}`))
      .map((item: HttpParam) => `${encodeURIComponent(item.key)}=${encodeURIComponent(String(item.value))}`)
      .join('&');
    return `${this.baseUrl}${resolved}${query.length > 0 ? '?' + query : ''}`;
  }

  private async requestJson(url: string, method: http.RequestMethod, body?: Object): Promise<Object> {
    if (NetworkConfig.useMock) {
      try {
        return JSON.parse(MockServer.responseFor(url)) as Object;
      } catch (err) {
        throw new NetworkError(url, `Mock response parse failed: ${JSON.stringify(err)}`);
      }
    }
    const request = http.createHttp();
    try {
      const requestOptions: http.HttpRequestOptions = {
        method: method
      };
      if (body !== undefined) {
        const headers: Record<string, string> = {};
        headers['Content-Type'] = 'application/json';
        requestOptions.header = headers;
        requestOptions.extraData = JSON.stringify(body);
      }
      const response = await request.request(url, requestOptions);
      const statusCode = Number(response.responseCode || 0);
      if (statusCode >= 400) {
        throw new NetworkError(url, `HTTP request failed with status ${statusCode}`, statusCode);
      }
      if (typeof response.result === 'string') {
        try {
          return JSON.parse(response.result) as Object;
        } catch (err) {
          throw new NetworkError(url, `HTTP response parse failed: ${JSON.stringify(err)}`, statusCode);
        }
      }
      return response.result as Object;
    } catch (err) {
      if (err instanceof NetworkError) {
        throw err;
      }
      throw new NetworkError(url, JSON.stringify(err));
    } finally {
      request.destroy();
    }
  }
}
