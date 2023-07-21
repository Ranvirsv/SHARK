//
//  AppDelegate.m
//  Updater_Shark
//
//  Created by Ranvir Singh Virk on 7/17/23.
//

#import "AppDelegate.h"
#import <Sparkle/Sparkle.h>
#import "GitHubClient.h"

@interface AppDelegate ()

@property (nonatomic) SPUStandardUpdaterController *updaterController;

@end

@implementation AppDelegate
- (void)feedURLStringWithCompletion:(void (^)(NSString * _Nullable downloadURL))completion{
    GitHubClient *client = [[GitHubClient alloc] init];
    [client getLatestReleaseForRepo:^(GitHubRelease *release, NSError *error){
        if (error) {
            NSLog(@"Error: %@", error);
            completion(nil);
        } else{
            completion(release.downloadURL);
        }
    }];
}

- (nullable NSString *)feedURLStringForUpdater:(nonnull SPUUpdater *)updater{
    __block NSString *downloadURL;
    
    dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);
    [self feedURLStringWithCompletion:^(NSString * _Nullable url) {
        downloadURL = url;
        dispatch_semaphore_signal(semaphore);
    }];
    
    dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);
    return @"https://www.dropbox.com/e/scl/fi/10j1isjruy3iuwzh9v9r3/DMG_Assembly.dmg";
}

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
    // Create the updater object
    self.updaterController = [[SPUStandardUpdaterController alloc] initWithUpdaterDelegate:self userDriverDelegate:self];
    [self feedURLStringForUpdater: self.updaterController.updater];
    [self.updaterController.updater checkForUpdates];
}


- (void)applicationWillTerminate:(NSNotification *)aNotification {
    // Insert code here to tear down your application
}


- (BOOL)applicationSupportsSecureRestorableState:(NSApplication *)app {
    return YES;
}


@end
