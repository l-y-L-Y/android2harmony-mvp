@Entry
@Component
struct About {
  build() {
    Stack({ alignContent: Alignment.BottomCenter }) {
      Text('OSChina.NET for Android')
        .fontSize(16)
        .fontWeight(FontWeight.Bold)
        .fontColor(Color.Black)
        .position({ y: -200 })

      Text('版本：1.0.0')
        .fontColor(Color.Black)
        .position({ y: -160 })

      Button('检查新版本')
        .width(100)
        .height(40)
        .backgroundColor('#4CAF50')
        .fontColor(Color.White)
        .position({ y: -110 })

      Text('Copyright ©2008-2012 奥思网络版权所有')
        .fontColor(Color.Black)
        .position({ y: -30 })
    }
    .width('100%')
    .height('100%')
    .backgroundImage($r('app.media.about_bg'))
    .backgroundImageSize(ImageSize.Cover)
  }
}