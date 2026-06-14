import { router } from '@kit.ArkUI';

interface MusicItem {
  title: string;
  artist: string;
  coverImg: string;
}

@Entry
@Component
export struct FragmentMain {
  @State currentTab: number = 0;
  @State musicList: MusicItem[] = [
    { title: '平凡的一天', artist: '毛不易', coverImg: 'bg_album_default' },
    { title: '消愁', artist: '毛不易', coverImg: 'bg_album_default' },
    { title: '起风了', artist: '买辣椒也用券', coverImg: 'bg_album_default' },
    { title: '可能否', artist: '木小雅', coverImg: 'bg_album_default' },
    { title: '纸短情长', artist: '烟把儿乐队', coverImg: 'bg_album_default' },
    { title: '我们不一样', artist: '大壮', coverImg: 'bg_album_default' },
    { title: '体面', artist: '于文文', coverImg: 'bg_album_default' },
    { title: '遥远的她', artist: '陈奕迅', coverImg: 'bg_album_default' }
  ];

  build() {
    Column() {
      // Scrollable content area (simulates CoordinatorLayout)
      Scroll() {
        Column() {
          // CollapsingToolbarLayout: background image
          Stack({ alignContent: Alignment.Bottom }) {
            Image($r('app.media.bg_home'))
              .width('100%')
              .height(275)
              .objectFit(ImageFit.Cover)

            // Toolbar
            Row() {
              // Menu icon
              Image($r('app.media.foreground'))
                .width(24)
                .height(24)
                .objectFit(ImageFit.Contain)
                .onClick(() => {
                  router.pushUrl({ url: 'pages/FragmentDrawer' });
                })

              // App icon
              Image($r('app.media.foreground'))
                .width(24)
                .height(24)
                .objectFit(ImageFit.Contain)
                .margin({ left: 8 })
                .onClick(() => {
                  router.pushUrl({ url: 'pages/FragmentLogin' });
                })

              // App name
              Text('PureMusic')
                .fontSize(18)
                .fontWeight(FontWeight.Bold)
                .fontColor('#000000')
                .layoutWeight(1)
                .textAlign(TextAlign.Center)
                .onClick(() => {
                  router.pushUrl({ url: 'pages/FragmentLogin' });
                })

              // Search icon
              Image($r('app.media.foreground'))
                .width(24)
                .height(24)
                .objectFit(ImageFit.Contain)
                .margin({ right: 12 })
                .onClick(() => {
                  router.pushUrl({ url: 'pages/FragmentSearch' });
                })
            }
            .width('100%')
            .height(48)
            .padding({ left: 12, right: 12 })
            .margin({ left: 12, right: 12, bottom: 12, top: 37 })
            .borderRadius(8)
            .backgroundColor(0x88FFFFFF)
            .borderWidth(1)
            .borderColor(0x33666666)
          }
          .width('100%')
          .height(275)

          // TabLayout
          Row() {
            Text('最近播放')
              .fontSize(16)
              .fontColor(this.currentTab === 0 ? '#808080' : '#CCCCCC')
              .fontWeight(this.currentTab === 0 ? FontWeight.Bold : FontWeight.Normal)
              .layoutWeight(1)
              .textAlign(TextAlign.Center)
              .height(44)
              .backgroundColor('#FFFFFF')
              .onClick(() => {
                this.currentTab = 0;
              })

            Text('最佳实践')
              .fontSize(16)
              .fontColor(this.currentTab === 1 ? '#808080' : '#CCCCCC')
              .fontWeight(this.currentTab === 1 ? FontWeight.Bold : FontWeight.Normal)
              .layoutWeight(1)
              .textAlign(TextAlign.Center)
              .height(44)
              .backgroundColor('#FFFFFF')
              .onClick(() => {
                this.currentTab = 1;
              })
          }
          .width('100%')

          // Tab indicator
          Row() {
            Divider()
              .width('50%')
              .height(4)
              .color('#808080')
              .offset({ x: this.currentTab === 0 ? 0 : '50%' })
          }
          .width('100%')

          // ViewPager content
          if (this.currentTab === 0) {
            // RecyclerView (playlist)
            ForEach(this.musicList, (item: MusicItem, index: number) => {
              Row() {
                // Cover image
                Image($r('app.media.foreground'))
                  .width(56)
                  .height(56)
                  .objectFit(ImageFit.Cover)
                  .borderRadius(4)

                // Title and artist
                Column() {
                  Text(item.title)
                    .fontSize(18)
                    .fontColor('#000000')
                    .maxLines(1)

                  Text(item.artist)
                    .fontSize(14)
                    .fontColor('#808080')
                    .maxLines(1)
                    .margin({ top: 4 })
                }
                .layoutWeight(1)
                .margin({ left: 12 })
                .alignItems(HorizontalAlign.Start)

                // Play status icon
                Image($r('app.media.ic_player'))
                  .width(36)
                  .height(36)
                  .objectFit(ImageFit.Contain)
                  .margin({ right: 12 })
                  .onClick(() => {
                    router.pushUrl({ url: 'pages/FragmentPlayer' });
                  })
              }
              .width('100%')
              .height(72)
              .padding({ left: 12, right: 0, top: 8, bottom: 8 })
              .onClick(() => {
                router.pushUrl({ url: 'pages/FragmentPlayer' });
              })
            })
          } else {
            // WebView (best practice)
            Column() {
              Text('最佳实践内容')
                .fontSize(16)
                .fontColor('#333333')
                .padding(16)
            }
            .width('100%')
            .height('100%')
          }
        }
      }
      .width('100%')
      .layoutWeight(1)
      .scrollBar(BarState.Off)
    }
    .width('100%')
    .height('100%')
  }
}