//
//  GitHubRelease.h
//  Updater_Shark
//
//  Created by Ranvir Singh Virk on 7/17/23.
//

#ifndef GitHubRelease_h
#define GitHubRelease_h

#import <Foundation/Foundation.h>

@interface GitHubRelease : NSObject

@property (nonatomic, strong) NSString *name;
@property (nonatomic, strong) NSString *tagName;
@property (nonatomic, strong) NSString *body;
@property (nonatomic, strong) NSString *downloadURL;

@end

#endif /* GitHubRelease_h */
