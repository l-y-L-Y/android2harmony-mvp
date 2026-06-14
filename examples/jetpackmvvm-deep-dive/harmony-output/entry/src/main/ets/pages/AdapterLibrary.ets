@Entry
@Component
export struct AdapterLibrary {
  @State libraryItems: LibraryInfo[] = [
    { title: '本项目中用到的技术点包括：', summary: '是难得一见的 Jetpack MVVM 最佳实践！' },
    { title: 'Jetpack 组件', summary: '使用 ViewModel、LiveData、DataBinding 等 Jetpack 组件构建应用架构。' },
    { title: '网络请求', summary: '使用 Retrofit2 + OkHttp3 + RxJava2 进行网络请求。' },
    { title: '图片加载', summary: '使用 Glide 加载网络图片和本地图片。' },
    { title: '音乐播放', summary: '使用 MediaPlayer 实现音乐播放和控制。' }
  ]

  build() {
    Column() {
      List({ space: 0 }) {
        ForEach(this.libraryItems, (item: LibraryInfo) => {
          ListItem() {
            Column() {
              Text(item.title)
                .fontSize(18)
                .fontWeight(FontWeight.Bold)
                .fontColor('#000000')
                .margin({ left: 16, top: 12 })
                .width('100%')
                .maxLines(1)
                .textOverflow({ overflow: TextOverflow.Ellipsis })

              Text(item.summary)
                .fontSize(13)
                .fontColor('#999999')
                .margin({ left: 16, top: 4, right: 16, bottom: 12 })
                .width('100%')
                .constraintSize({ maxWidth: 300 })
                .textOverflow({ overflow: TextOverflow.Ellipsis })
            }
            .width('100%')
            .backgroundColor('#FFFFFF')
            .stateStyles({
              normal: {
                .backgroundColor('#FFFFFF')
              },
              pressed: {
                .backgroundColor('#F5F5F5')
              }
            })
            .onClick(() => {
              // TODO: Navigate to item detail or perform action
            })
          }
        })
      }
      .width('100%')
      .height('100%')
      .divider({ strokeWidth: 0.5, color: '#E5E5E5', startMargin: 16, endMargin: 16 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#FFFFFF')
  }
}

interface LibraryInfo {
  title: string;
  summary: string;
}