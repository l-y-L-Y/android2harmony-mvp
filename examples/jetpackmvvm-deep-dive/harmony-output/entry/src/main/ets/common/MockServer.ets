export class MockEndpoint {
  module: string;
  path: string;
  source: string;

  constructor(module: string, path: string, source: string) {
    this.module = module;
    this.path = path;
    this.source = source;
  }
}

export class MockServer {
  static endpoints: MockEndpoint[] = [
  new MockEndpoint('app', 'xxx/login', 'D:\\codex\\android-benchmarks\\test5\\JetpackMVVM\\app\\src\\main\\java\\com\\kunminx\\puremusic\\data\\api\\AccountService.java'),
  ];
  static routes: string[] = [
  'pages/Index',
  'pages/MainActivity',
  'pages/AdapterLibrary',
  'pages/FragmentDrawer',
  'pages/FragmentLogin',
  'pages/FragmentMain',
  'pages/FragmentPlayer',
  'pages/FragmentSearch',
  'pages/NotifyPlayerBig',
  'pages/NotifyPlayerSmall',
  ];
  static items: string[] = ['Camera', 'Screenshots', 'Downloads', 'Favorites', 'Videos', 'Edited'];

  static sampleItems(): string[] {
    return MockServer.items;
  }

  static routeTitle(route: string): string {
    const name = route.split('/').pop() || route;
    return name.replace(/^Activity/, '').replace(/([a-z0-9])([A-Z])/g, '$1 $2') || 'Index';
  }

  static responseFor(path: string): string {
    if (path.indexOf('pokemon/{name}') >= 0 || path.indexOf('/pokemon/') >= 0) {
      return '{"id":1,"name":"Bulbasaur","height":7,"weight":69,"experience":64,"types":["grass","poison"],"hp":45,"attack":49,"defense":49,"speed":45,"exp":64}';
    }
    if (path.indexOf('pokemon') >= 0) {
      return '{"count":10,"next":null,"previous":null,"results":[{"page":0,"name":"Bulbasaur","url":"https://pokeapi.co/api/v2/pokemon/1/"},{"page":0,"name":"Ivysaur","url":"https://pokeapi.co/api/v2/pokemon/2/"},{"page":0,"name":"Venusaur","url":"https://pokeapi.co/api/v2/pokemon/3/"},{"page":0,"name":"Charmander","url":"https://pokeapi.co/api/v2/pokemon/4/"}]}';
    }
    return '{"generated":true,"items":["Camera","Screenshots","Downloads","Favorites"]}';
  }
}
