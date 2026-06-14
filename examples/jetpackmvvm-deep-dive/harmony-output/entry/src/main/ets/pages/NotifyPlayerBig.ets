import { router } from '@kit.ArkUI';

interface NotifyPlayerState {
  songName: string;
  authorName: string;
  albumName: string;
  isPlaying: boolean;
}

@Entry
@Component
export struct NotifyPlayerBig {
  @State songName: string = '夜曲';
  @State authorName: string = '周杰伦';
  @State albumName: string = '十一月的萧邦';
  @State isPlaying: boolean = true;

  build() {
    Row() {
      // Album art area (128x128)
      Stack({ alignContent: Alignment.Center }) {
        Image($r('app.media.bg_album_default'))
          .width(128)
          .height(128)
          .objectFit(ImageFit.Fill)
          .backgroundColor('#ffc0c0c0')

        LoadingProgress()
          .width(30)
          .height(30)
      }
      .width(128)
      .height(128)

      // Right content area
      Stack({ alignContent: Alignment.Bottom }) {
        // Top section: song info + close
        Column() {
          Row() {
            Column() {
              Text(this.songName)
                .width('100%')
                .fontSize(14)
                .fontColor('#ffffffff')
                .maxLines(1)
                .margin({ left: 12, top: 4 })

              Text(this.authorName)
                .width('100%')
                .fontSize(14)
                .fontColor('#ffffffff')
                .maxLines(1)
                .margin({ left: 12, top: 1 })

              Text(this.albumName)
                .width('100%')
                .fontSize(14)
                .fontColor('#ffffffff')
                .maxLines(1)
                .margin({ left: 12, top: 1 })
            }
            .layoutWeight(1)
            .alignItems(HorizontalAlign.Start)

            // Close button
            Image($r('app.media.ic_close_white'))
              .width(44)
              .height(44)
              .objectFit(ImageFit.CENTER)
              .padding(10)
              .onClick(() => {
                // TODO: close notification action
              })
          }
          .width('100%')
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Start)

        // Bottom control bar area
        Column() {
          // Divider line
          Divider()
            .width('100%')
            .height(0.5)
            .color('#ff808080')

          // Player controls
          Row() {
            // Previous
            Image($r('app.media.ic_next_dark'))
              .width(40)
              .height(40)
              .objectFit(ImageFit.CENTER)
              .margin({ left: 10, right: 10 })
              .onClick(() => {
                // TODO: previous track action
              })

            // Pause (visible when playing)
            if (this.isPlaying) {
              Image($r('app.media.ic_action_pause'))
                .width(40)
                .height(40)
                .objectFit(ImageFit.CENTER)
                .margin({ left: 10, right: 10 })
                .onClick(() => {
                  this.isPlaying = false;
                })
            }

            // Play (visible when paused)
            if (!this.isPlaying) {
              Image($r('app.media.ic_action_play'))
                .width(40)
                .height(40)
                .objectFit(ImageFit.CENTER)
                .margin({ left: 10, right: 10 })
                .onClick(() => {
                  this.isPlaying = true;
                })
            }

            // Next
            Image($r('app.media.ic_previous_dark'))
              .width(40)
              .height(40)
              .objectFit(ImageFit.CENTER)
              .margin({ left: 10, right: 10 })
              .onClick(() => {
                // TODO: next track action
              })
          }
          .width('100%')
          .height(48)
          .justifyContent(FlexAlign.Center)
          .alignItems(VerticalAlign.Center)
        }
        .width('100%')
      }
      .layoutWeight(1)
      .height(128)
    }
    .width('100%')
    .height(128)
    .backgroundColor('#ffe0e0e0')
  }
}