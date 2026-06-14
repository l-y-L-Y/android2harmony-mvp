@Entry
@Component
export struct FragmentDrawer {
  @State list: LibraryInfo[] = []
  
  aboutToAppear() {
    // Simulate fetching library info data
    this.list = [
      { name: "PureMusic", version: "1.0.0", description: "是难得一见的 Jetpack MVVM 最佳实践！" },
      { name: "Architecture", version: "1.0.0", description: "提供 MVVM 架构组件支持" },
      { name: "BindingRecyclerView", version: "1.0.0", description: "提供 RecyclerView 的 DataBinding 支持" }
    ]
  }
  
  build() {
    Column() {
      // Logo
      Image($r('app.media.ic_launcher'))
        .width(100)
        .height(100)
        .margin({ top: 40 })
        .onClick(() => {
          // TODO: Open project link in browser
        })
      
      // App name
      Text($r('app.string.app_name'))
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
        .fontColor('#000000')
        .margin({ top: 16 })
        .onClick(() => {
          // TODO: Open project link in browser
        })
      
      // App summary
      Text($r('app.string.app_summary'))
        .fontSize(12)
        .fontColor('#AAAAAA')
        .margin({ top: 16 })
        .onClick(() => {
          // TODO: Open project link in browser
        })
      
      // Library list
      List() {
        ForEach(this.list, (item: LibraryInfo) => {
          ListItem() {
            Column() {
              Row() {
                Text(item.name)
                  .fontSize(16)
                  .fontWeight(FontWeight.Bold)
                  .fontColor('#000000')
                  .layoutWeight(1)
                
                Text(item.version)
                  .fontSize(14)
                  .fontColor('#888888')
              }
              .width('100%')
              
              Text(item.description)
                .fontSize(12)
                .fontColor('#AAAAAA')
                .margin({ top: 4 })
                .maxLines(2)
            }
            .width('100%')
            .padding({ left: 16, right: 16, top: 12, bottom: 12 })
          }
        })
      }
      .layoutWeight(1)
      .margin({ top: 24 })
      .divider({ strokeWidth: 0.5, color: '#EEEEEE' })
      
      // Copyright
      Text($r('app.string.Copyright'))
        .fontSize(12)
        .fontColor('#AAAAAA')
        .height(48)
        .width('100%')
        .textAlign(TextAlign.Center)
        .backgroundColor('#FFFFFF')
        .onClick(() => {
          // TODO: Open project link in browser
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#FFFFFF')
  }
}

interface LibraryInfo {
  name: string
  version: string
  description: string
}