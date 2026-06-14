import { NavigationCompat } from '../common/NavigationCompat';

@Entry
@Component
struct Index {
  aboutToAppear(): void { NavigationCompat.replace(this, { url: 'pages/MainActivity' }); }

  build() {
    Column() {
      Text('PureMusic')
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 8 })
      Button('进入')
        .width(160)
        .height(44)
        .margin({ top: 24 })
        .onClick(() => { NavigationCompat.replace(this, { url: 'pages/MainActivity' }); })

    }
    .width('100%')
    .height('100%')
    .padding(24)
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}
